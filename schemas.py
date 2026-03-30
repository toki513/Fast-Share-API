from pydantic import BaseModel
from datetime import datetime

class PostCreate(BaseModel):
     title:str
     content:str
     
class PostResponse(BaseModel):
     id:int
     caption:str
     url:str|None
     created_at:datetime
     file_name:str
     file_type:str
     
     class Config:
          from_attributes = True
          
          
class UploadFileResult(BaseModel):
    url: str
    caption: str

    class Config:
        extra = "allow" 