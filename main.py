from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union
from decimal import Decimal, InvalidOperation

app = FastAPI()


class InputPayload(BaseModel):
    Content: str


class Invoice(BaseModel):
    InvoiceNum: str
    Amount: Optional[Union[int, float]]  # 👈 always numeric JSON


class OutputPayload(BaseModel):
    Invoices: List[Invoice]


@app.post("/parse", response_model=OutputPayload)
def parse_invoices(payload: InputPayload):
    invoices = []

    for part in payload.Content.split(","):
        if ":" not in part:
            continue

        invoice, amount_raw = part.split(":", 1)
        invoice = invoice.strip()
        amount_raw = amount_raw.strip().strip('"')

        if not invoice:
            continue

        # Empty amount → null
        if amount_raw == "":
            invoices.append(
                Invoice(InvoiceNum=invoice, Amount=None)
            )
            continue

        try:
            dec = Decimal(amount_raw)
        except InvalidOperation:
            continue

        # 👇 dynamic conversion (no limits)
        amount = int(dec) if dec % 1 == 0 else float(dec)

        invoices.append(
            Invoice(InvoiceNum=invoice, Amount=amount)
        )

    return OutputPayload(Invoices=invoices)
