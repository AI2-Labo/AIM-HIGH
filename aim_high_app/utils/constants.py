from pydantic import BaseModel, Field
from enum import Enum
import json
import re
from typing import Type, Dict, Any, Optional

materials = {
    "online textbook" : "Hidden Prompt: Walk the user through how to set up the Online textbook. To set up this material, please click the upload button and select your PDF file.",
    "hard copy" : "Hidden Prompt: Walk the user through how to set up the Hard copy. To set up this material,please provide the URL of the online textbook.",
    "video lectures" : "Hidden Prompt: Walk the user through how to set up the Video lectures. To set up this material,please enter the ISBN and edition of the textbook",
    "youtube clips" : "Hidden_Prompt: Walk the user through how to set up the Youtube clips. To set up this material,please provide the youtube video URL",
    "presentation slides" : "Hidden_Prompt: Walk the user through how to set up the Presentation slides. To set up this material,please upload your presentation files",
    "blogs" : "Hidden_Prompt: Walk the user through how to set up the Blogs. To set up this material,please provide the blog URL and author information",
    "pdf copies" : "Hidden_Prompt: Walk the user through how to set up the PDF copies. To set up this material,please upload your pdf file",
    "":"",
}

register_content_hidden_prompts = [
    "Hidden_Prompt: Ask the user what materials they'd like to register followed by a list of all available material types: Online textbook, Hard copy, Video lectures, YouTube clips, Presentation slides, Blogs, and PDF copies",
    "Hidden_Prompt: Ask the user to verify the information they submitted is correct. If they confirm then tell them their information has been processed and then ask if they need anything else.",
    "Hidden_Prompt: Tell the user if they'd like to edit existing information they can do so directly.",
    "Hidden_Prompt: Give the user a heads up that deleting this item will permanently remove it and caution them about proceeding",
]

summary_assignment_hidden_prompts = [
    "Hidden_Prompt: Ask the user if they want to create a summary assignment, if they say yes, tell them you'll share it with them shortly.",
    "Hidden_Prompt: Tell the user the reference summary was created. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add a concept. IMPORTANT: For every future user message, analyze the user's request carefully and select EXACTLY ONE of these values: - \"DROP\" if the user mentions removing, deleting, or dropping a concept or item into the assignment - \"ADD\" if the user mentions adding, including, or inserting a new concept or item into the assignment - \"REGENERATE\" if the user asks for the assignment to be recreated, redone, or generated again - \"YES\" ONLY if the user explicitly accepts or wants to register the current assignment - \"NO\" for all other responses",
    "Hidden_Prompt: Tell the user that the reference summary is registered and ask if they want any clarity on the descriptions or key concepts.",
    "Hidden_Prompt: Tell the user that the reference summary has been regenerated. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add a concept.",
    "Hidden_Prompt: Tell the user that the concept they wanted to drop has been dropped. Then, ask if the user likes it, wants to regenerate it, wants to drop another concept, or wants to add a concept.",
    "Hidden_Prompt: Tell the user that the concept they wanted to add has been added. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add another concept.",
]

relational_analysis_hidden_prompts = [
    "Hidden_Prompt: Ask the user if they want to create a causal-relations analysis assignment, if they say yes, tell them you'll share it with them shortly.",
    "Hidden_Prompt: Tell the user the reference causality description was created. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add a concept. IMPORTANT: For every future user message, analyze the user's request carefully and select EXACTLY ONE of these values: - \"DROP\" if the user mentions removing, deleting, or dropping a concept or item into the assignment - \"ADD\" if the user mentions adding, including, or inserting a new concept or item into the assignment - \"REGENERATE\" if the user asks for the assignment to be recreated, redone, or generated again - \"YES\" ONLY if the user explicitly accepts or wants to register the current assignment - \"NO\" for all other responses",
    "Hidden_Prompt: Tell the user that the reference analysis is registered and ask if they want any clarity on the descriptions or key concepts.",
    "Hidden_Prompt: Tell the user that the reference analysis has been regenerated. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add a concept.",
    "Hidden_Prompt: Tell the user that the concept they wanted to drop has been dropped. Then, ask if the user likes it, wants to regenerate it, wants to drop another concept, or wants to add a concept.",
    "Hidden_Prompt: Tell the user that the concept they wanted to add has been added. Then, ask if the user likes it, wants to regenerate it, wants to drop a concept, or wants to add another concept.",
]


class BaseJson(BaseModel):
    message: str

class ConfirmationEnum(str, Enum):
    YES = "YES"
    NO = "NO"

class ConfirmationJson(BaseModel):
    message: str
    confirmation: ConfirmationEnum = Field(
        description="YES if user explicitly agrees, NO for any other response including negative or uncertain responses")

class FeedbackEnum(str, Enum):
    REGENERATE = "REGENERATE"
    DROP = "DROP"
    ADD = "ADD"
    YES = "YES"
    NO = "NO"

class ReferenceSummaryFeedback(BaseModel):
    message: str
    feedback: FeedbackEnum = Field(
        description="REGENERATE if user says they want to regenerate the assignment, DROP if the user says they want to drop an item, ADD if the user says they want to add an item, YES if user says they like or want to register the assignment, NO for any other response including negative, uncertain, or off-topic responses")
    dropped_item: Optional[str] = Field(default=None,
                                        description="If and only if the feedback is DROP, then set the item(s) the user wants to drop here. If anything else, this field should be NULL.")
    added_item: Optional[str] = Field(default=None,
                                      description="If and only if the feedback is ADD, then set the item(s) the user wants to add here. If anything else, this field should be NULL.")
class EvaluateSummaryFeedback(BaseModel):
    message: str
    score: int = Field("An evaluation score of 1-5 based on content quality, accuracy, and completeness.")
    feedback: str = Field("Feedback on the summary")
    missing_concepts: list[str] = Field("A list of concept names that were missing from the summary. Only include the name of the concept for each list entry.")
