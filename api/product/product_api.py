import base64
import json
import os
import shutil
import sys
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
from starlette.responses import JSONResponse

from auth.helper import get_current_user
from db.db import get_db
from models.product.product import Product
from models.user.user import User
from repository.change_log.change_log_repository import ChangeLogRepository
from repository.product.product_repository import ProductRepository
from schema.invoice.invoice_schema import InvoiceData, StockOutRequestList, PDFFileData
from schema.product.product_schema import ProductCreate, ProductUpdate, ChangeLog, ProductDeleteResponse

router = APIRouter()

UPLOAD_DIR = Path("uploads")

UPLOAD_PDF_DIR = "static/pdfs"

if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir(parents=True)


@router.post("/add/", response_model=ProductCreate)
async def create_new_product(
        current_user: User = Depends(get_current_user),
        name: str = Form(...),
        code: str = Form(...),
        stock: int = Form(None),
        date_added: str = Form(...),
        brand: str = Form(None),
        model: str = Form(None),
        mt: str = Form(None),
        m2: str = Form(None),
        m3: str = Form(None),
        ton: str = Form(None),
        kg: str = Form(None),
        adet: str = Form(None),
        delivered_by: str = Form(None),
        delivered_to: str = Form(None),
        description: str = Form(None),
        warehouse: str = Form(None),
        file: UploadFile = File(None),
        db: Session = Depends(get_db)
):
    print(current_user.name)
    image_path = None
    if file:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_location = UPLOAD_DIR / f"{timestamp}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_path = str(file_location)

    def to_int_or_none(value):
        return int(value) if value and value.isdigit() else None

    product_data = ProductCreate(
        name=name,
        code=code,
        stock=stock,
        brand=brand,
        model=model,
        mt=to_int_or_none(mt),
        m2=to_int_or_none(m2),
        m3=to_int_or_none(m3),
        ton=to_int_or_none(ton),
        kg=to_int_or_none(kg),
        adet=to_int_or_none(adet),
        added_by=current_user.name,
        date_added=date_added,
        delivered_by=delivered_by,
        delivered_to=delivered_to,
        description=description,
        warehouse=warehouse,
        image=image_path
    )

    product_repo = ProductRepository(db)
    return product_repo.create(product_data)


@router.get("/list/")
def read_products(db: Session = Depends(get_db)):
    product_repo = ProductRepository(db)
    return product_repo.get_all()


@router.delete("/{product_code}/", response_model=ProductDeleteResponse)
def delete_product(product_code: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), ):
    product_repo = ProductRepository(db)

    product = product_repo.get_by_code(product_code)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    changes = [{"field": "product", "old_value": product.name, "new_value": "Ürün Silindi"}]

    product_repo.delete(product.id)

    product_repo.log_changes(product_code, changes, current_user.name)

    return {"message": f"Product {product.name} (code: {product.code}) has been deleted."}


@router.put("/stock-in/update/{product_id}/", response_model=ProductCreate)
def update_product(
        product_id: str,
        product_data: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    product_repo = ProductRepository(db)

    try:
        updated_product = product_repo.update_product(product_id, product_data.dict(exclude_unset=True),
                                                      current_user.name)
    except HTTPException as e:
        raise e
    return updated_product


@router.get("/change-log/", response_model=list[ChangeLog])
def read_change_logs(db: Session = Depends(get_db)):
    change_log_repo = ChangeLogRepository(db)
    return change_log_repo.get_all_change_logs()


@router.post("/upload-logo/")
async def upload_logo(file: UploadFile = File(...)):
    # PyInstaller geçici dizinini kontrol eden fonksiyon
    def get_static_directory():
        if getattr(sys, 'frozen', False):
            # PyInstaller ile çalışıyorsak geçici dizini kullan
            base_dir = sys._MEIPASS
        else:
            # Normal çalışma dizini
            base_dir = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_dir, "static")

    # Statik dizini al
    BASE_DIR = get_static_directory()
    UPLOAD_DIRECTORY = os.path.join(BASE_DIR, "logos")

    try:
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)

        for filename in os.listdir(UPLOAD_DIRECTORY):
            file_path = os.path.join(UPLOAD_DIRECTORY, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Yeni logo dosyasını kaydet
        file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        return {"success": True, "file_path": file_location}

    except Exception as e:
        print(e)
        return {"success": False, "error": str(e)}


@router.get("/invoice-data/")
async def get_invoice_data():
    try:
        with open("static/invoice_data.json", "r", encoding="utf-8") as f:
            invoice_data = json.load(f)

        upload_directory = "static/logos"
        logo_files = os.listdir(upload_directory)
        print(logo_files)

        if logo_files:
            logo_path = f"/static/logos/{logo_files[0]}"

            if os.path.exists(os.path.join(upload_directory, logo_files[0])):
                invoice_data["logo_path"] = logo_path
                print("çıktım")
                print(invoice_data["logo_path"])
            else:
                invoice_data["logo_path"] = None
        else:
            invoice_data["logo_path"] = None

        return JSONResponse(content=invoice_data)

    except FileNotFoundError:
        return JSONResponse(content={"message": "Invoice data not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)


@router.post("/invoice-data/")
async def save_invoice_data(invoice_data: InvoiceData):
    upload_directory = "static/logos"
    logo_files = os.listdir(upload_directory)

    logo_path = None
    if logo_files:
        logo_path = f"{upload_directory}/{logo_files[0]}"

    invoice_data_with_logo = invoice_data.dict()
    if logo_path:
        invoice_data_with_logo["logo_path"] = logo_path
    simplified_products = [
        {
            "name": product["name"],
            "stockOut": product["stockOut"],
            "unit": product["unit"],
            "code": product["code"]
        }
        for product in invoice_data_with_logo["products"]
    ]

    with open("static/invoice_data.json", "w", encoding="utf-8") as f:
        json.dump({"invoice": invoice_data_with_logo, "products": simplified_products}, f)

    return {"message": "Invoice data saved", "pdf_url": "/static/invoice.html"}


@router.post("/invoice/save-pdf/")
async def save_pdf_file(file_data: PDFFileData):
    try:
        if not os.path.exists(UPLOAD_PDF_DIR):
            os.makedirs(UPLOAD_PDF_DIR)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{file_data.fileName}_{timestamp}.pdf"
        file_path = os.path.join(UPLOAD_PDF_DIR, file_name)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(file_data.file))

        return {"message": "PDF dosyası başarıyla kaydedildi", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF dosyası kaydedilirken hata oluştu: {e}")


@router.get("/pdfs/")
async def list_pdfs():
    try:
        files = [f for f in os.listdir(UPLOAD_PDF_DIR) if f.endswith(".pdf")]
        file_list = [{"fileName": file, "filePath": f"/{UPLOAD_PDF_DIR}/{file}"} for file in files]
        return file_list
    except Exception as e:
        return {"message": f"Error fetching invoice files: {e}"}


@router.post("/finalize-stock-out/")
async def finalize_stock_out(request: StockOutRequestList, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_user)):
    product_repo = ProductRepository(db)

    try:
        for item in request.products:
            product = product_repo.get_by_code(item.code)

            if item.unit == "MT":
                old_stock = int(product.mt) if product.mt is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for MT in product code {item.code}")
                product_data = {"mt": new_stock}

            elif item.unit == "KG":
                old_stock = int(product.kg) if product.kg is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for KG in product code {item.code}")
                product_data = {"kg": new_stock}

            elif item.unit == "M2":
                old_stock = int(product.m2) if product.m2 is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for M2 in product code {item.code}")
                product_data = {"m2": new_stock}

            elif item.unit == "Stok":
                old_stock = int(product.stock) if product.stock is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for M2 in product code {item.code}")
                product_data = {"stock": new_stock}

            elif item.unit == "M3":
                old_stock = int(product.m3) if product.m3 is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for M3 in product code {item.code}")
                product_data = {"m3": new_stock}

            elif item.unit == "Ton":
                old_stock = int(product.ton) if product.ton is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for TON in product code {item.code}")
                product_data = {"ton": new_stock}

            elif item.unit == "Adet":
                old_stock = int(product.adet) if product.adet is not None else 0
                new_stock = old_stock - item.stock_out
                # if new_stock < 0:
                #    raise HTTPException(status_code=400,
                #                        detail=f"Insufficient stock for Adet in product code {item.code}")
                product_data = {"adet": new_stock}

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported unit: {item.unit}")

            product_repo.update_stock_out_product(product_code=item.code, product_data=product_data,
                                                  updated_by=current_user.name)

        return {"message": "Stock out process completed successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
