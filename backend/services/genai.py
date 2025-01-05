from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptAvailable
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAI
from vertexai.generative_models import GenerativeModel
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from tqdm import tqdm
import re
import json
import logging
import urllib.parse

# Configure log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiProcessor:
    def __init__(self, model_name, project):
        self.model = VertexAI(model_name=model_name, project=project)
    
    def generate_documents_summary(self, documents: list, **args):
        try:
            if not documents:
                logger.error("No documents provided for summary generation")
                return None
                
            chain_type = "map_reduce" if len(documents) > 10 else "stuff"
            chain = load_summarize_chain(
                chain_type=chain_type,
                llm=self.model,
                **args
            )
            return chain.run(documents)
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return None

    def count_total_tokens(self, docs: list):
        if not docs:
            return 0
            
        temp_model = GenerativeModel("gemini-1.5-flash-002")
        total = 0
        logger.info("Counting total billable characters...")
        for doc in tqdm(docs):
            total += temp_model.count_tokens(doc.page_content).total_billable_characters
        return total

    def get_model(self):
        return self.model

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    try:
        # Handle different URL formats
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
            return parsed_url.path[1:]
        if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
            query = urllib.parse.parse_qs(parsed_url.query)
            return query['v'][0]
    except Exception as e:
        logger.error(f"Failed to extract video ID from URL: {e}")
        raise ValueError(f"Invalid YouTube URL: {url}")
    
class YoutubeProcessor:
    def __init__(self, genai_processor: GeminiProcessor):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=0
        )
        self.genai_processor = genai_processor

    def retrieve_youtube_documents(self, video_url: str, verbose=False) -> list:
        """Retrieve and process YouTube video transcript."""
        try:
            # Extract video ID
            video_id = extract_video_id(video_url)
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            
            if not transcript_list:
                logger.error("No transcript available for video")
                return []
            
            # Combine transcript entries into a single text
            full_transcript = " ".join(entry['text'] for entry in transcript_list)
            
            # Create a Document object
            doc = Document(
                page_content=full_transcript,
                metadata={"source": video_url}
            )
            
            # Split the document
            result = self.text_splitter.split_documents([doc])
            
            if verbose:
                logger.info(f"Retrieved transcript for video ID: {video_id}")
                logger.info(f"Split into {len(result)} chunks")
                total_billable_characters = self.genai_processor.count_total_tokens(result)
                logger.info(f"Total Billable Characters: {total_billable_characters}")
            
            return result
            
        except (TranscriptsDisabled, NoTranscriptAvailable) as e:
            logger.error(f"No transcript available: {e}")
            return []
        except ValueError as e:
            logger.error(f"Invalid URL: {e}")
            return []
        except Exception as e:
            logger.error(f"Error retrieving video transcript: {e}")
            return []

    def find_key_concepts(self, documents: list, sample_size: int = 0, verbose=False):
        try:
            # Check if no documents were provided
            if not documents:
                logger.error("No documents provided to find key concepts.")
                return []

            # Set a default sample size if it's zero
            if sample_size == 0:
                sample_size = max(1, len(documents) // 5)
                if verbose:
                    logger.info(f"No sample size specified. Setting sample size to: {sample_size}")

            # Handle edge case where sample size is larger than the number of documents
            sample_size = min(sample_size, len(documents))

            # Find the number of documents in each group
            num_docs_per_group = max(1, len(documents) // sample_size)

            # Check thresholds for response quality
            if num_docs_per_group >= 10:
                logger.warning("Each group has more than 10 documents, output quality may degrade.")
            elif num_docs_per_group > 5:
                logger.warning("Each group has more than 5 documents, consider increasing the sample size.")

            # Split the documents into groups
            groups = [documents[i:i+num_docs_per_group] for i in range(0, len(documents), num_docs_per_group)]

            batch_concepts = []
            batch_cost = 0

            logger.info("Finding key concepts...")
            for group in tqdm(groups):
                # Combine content for documents per group
                group_content = " ".join(doc.page_content for doc in group)

                # Prompt for finding concepts
                prompt = PromptTemplate(
                    template="""
                    Find and define key concepts and definitions found in the following text:
                    {text}
                    Respond only in clean JSON format without any labels or additional text. The output needs to look exactly like this:
                    {{"concept1": "definition1", "concept2": "definition2", ...}}
                    """,
                    input_variables=["text"]
                )

                # Create and run chain
                chain = prompt | self.genai_processor.model
                output_concept = chain.invoke({"text": group_content})

                # Clean and process the output
                cleaned_json = self._clean_json_string(output_concept)
                if cleaned_json:
                    try:
                        concepts_dict = json.loads(cleaned_json)
                        batch_concepts.append(concepts_dict)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON: {e}")

                # Log processing details if verbose
                if verbose:
                    self._log_processing_details(group_content, output_concept, batch_cost)

            return batch_concepts

        except Exception as e:
            logger.error(f"Error in find_key_concepts: {e}")
            return []

    def _clean_json_string(self, json_str):
        """Clean JSON String capturing only the value between curly braces"""
        pattern = r'^.*?({.*}).*$'
        matches = re.findall(pattern, json_str, re.DOTALL)
        return matches[0] if matches else None

    def _log_processing_details(self, input_content, output_content, batch_cost):
        input_char = len(input_content)
        input_cost = (input_char/1000) * 0.000125
        output_char = len(output_content)
        output_cost = (output_char/1000) * 0.000375
        
        logger.info(f"Input characters: {input_char}")
        logger.info(f"Input cost: ${input_cost:.6f}")
        logger.info(f"Output characters: {output_char}")
        logger.info(f"Output cost: ${output_cost:.6f}")
        logger.info(f"Total cost: ${(input_cost + output_cost):.6f}\n")
        
        return input_cost + output_cost