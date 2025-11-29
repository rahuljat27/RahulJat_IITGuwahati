from pydantic import BaseModel, Field
from typing import List, Literal

class BillItem(BaseModel):
    item_name: str = Field(description="Name of the item exactly as mentioned")
    item_amount: float = Field(description="Net amount of the item")
    item_rate: float = Field(description="Unit rate of the item")
    item_quantity: float = Field(description="Quantity of the item (e.g., 1.00, 0.75)")

class PageData(BaseModel):
    page_no: str = Field(description="The page number extracted from the text headers")
    page_type: Literal["Bill Detail", "Final Bill", "Pharmacy"] = Field(description="Type of bill page")
    bill_items: List[BillItem]

class BillData(BaseModel):
    pagewise_line_items: List[PageData]
    total_item_count: int = Field(description="Total count of all items across all pages")

class FinalResponse(BaseModel):
    data: BillData