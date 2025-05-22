from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx
import json
from datetime import datetime
import stripe
import os
from enum import Enum

# Configuración
app = FastAPI(
    title="FERREMAS Integration API",
    description="API de integración para FERREMAS - Servicios web para gestión de productos, pagos y divisas",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de APIs externas
FERREMAS_API_URL = "https://ea2p2assets-production.up.railway.app"
FERREMAS_TOKEN = "SaGrP9ojGS39hU9ljqbXxQ=="
BCH_API_URL = "https://mindicador.cl/api"

# Security
security = HTTPBearer()

# Modelos Pydantic
class UserRole(str, Enum):
    ADMIN = "admin"
    MANTENEDOR = "mantenedor"
    JEFE_TIENDA = "jefe_tienda"
    BODEGA = "bodega"
    CLIENTE = "cliente"
    SERVICE_ACCOUNT = "service_account"

class User(BaseModel):
    username: str
    role: UserRole

class AuthRequest(BaseModel):
    username: str
    password: str

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category: str
    brand: Optional[str] = None
    code: Optional[str] = None
    is_promotion: bool = False
    is_novelty: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_promotion: Optional[bool] = None
    is_novelty: Optional[bool] = None

class Sucursal(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    city: str

class Vendedor(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    sucursal_id: int

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    items: List[OrderItem]
    customer_info: Dict[str, Any]
    payment_method: str = "stripe"

class ContactRequest(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    vendedor_id: int
    message: str

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "clp"
    payment_method_id: str
    customer_email: str

class CurrencyConversion(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

# Base de datos simulada de usuarios
USERS_DB = {
    "javier_thompson": {"password": "aONF4d6aNBIxRjlgjBRRzrS", "role": "admin"},
    "ignacio_tapia": {"password": "f7rWChmQS1JYfThT", "role": "cliente"},
    "stripe_sa": {"password": "dzkQqDL9XZH33YDzhmsf", "role": "service_account"}
}

# Funciones de utilidad
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Validar token y obtener usuario actual"""
    token = credentials.credentials
    
    # Verificar si es el token de FERREMAS
    if token == FERREMAS_TOKEN:
        return User(username="ferremas_system", role=UserRole.SERVICE_ACCOUNT)
    
    # Aquí deberías implementar la lógica real de validación de tokens
    # Por simplicidad, usamos una validación básica
    try:
        # Decodificar token (implementar JWT en producción)
        username = token  # Simplificado para el ejemplo
        if username in USERS_DB:
            return User(username=username, role=UserRole(USERS_DB[username]["role"]))
    except:
        pass
    
    raise HTTPException(status_code=401, detail="Token inválido")

def check_role_permission(user: User, required_roles: List[UserRole]):
    """Verificar permisos de rol"""
    if user.role not in required_roles:
        raise HTTPException(status_code=403, detail="Permisos insuficientes")

async def make_ferremas_request(endpoint: str, method: str = "GET", data: dict = None):
    """Realizar petición a la API de FERREMAS"""
    headers = {
        "Authorization": f"Bearer {FERREMAS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        url = f"{FERREMAS_API_URL}{endpoint}"
        
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=f"Error en API FERREMAS: {response.text}")
        
        return response.json()

# Endpoints de Autenticación
@app.post("/auth/login")
async def login(auth_request: AuthRequest):
    """Autenticar usuario y generar token"""
    user_data = USERS_DB.get(auth_request.username)
    
    if not user_data or user_data["password"] != auth_request.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # En producción, generar JWT token
    token = auth_request.username  # Simplificado para el ejemplo
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": auth_request.username,
            "role": user_data["role"]
        }
    }

# Endpoints de Productos
@app.get("/products/catalog", response_model=List[Product])
async def getCatalog(user: User = Depends(get_current_user)):
    """Obtener catálogo completo de productos"""
    return await make_ferremas_request("/products")

@app.get("/products/{product_id}", response_model=Product)
async def getProduct(product_id: int, user: User = Depends(get_current_user)):
    """Obtener producto específico por ID"""
    return await make_ferremas_request(f"/products/{product_id}")

@app.get("/products/promotions", response_model=List[Product])
async def getPromotions(user: User = Depends(get_current_user)):
    """Obtener productos en promoción"""
    products = await make_ferremas_request("/products")
    return [p for p in products if p.get("is_promotion", False)]

@app.get("/products/novelties", response_model=List[Product])
async def getNovelties(user: User = Depends(get_current_user)):
    """Obtener productos novedades"""
    products = await make_ferremas_request("/products")
    return [p for p in products if p.get("is_novelty", False)]

@app.post("/products", response_model=Product)
async def addProduct(product: Product, user: User = Depends(get_current_user)):
    """Agregar nuevo producto al catálogo"""
    check_role_permission(user, [UserRole.ADMIN, UserRole.MANTENEDOR])
    return await make_ferremas_request("/products", "POST", product.dict())

@app.put("/products/{product_id}/promotion")
async def markAsPromotion(product_id: int, is_promotion: bool, user: User = Depends(get_current_user)):
    """Marcar producto como promoción"""
    check_role_permission(user, [UserRole.ADMIN, UserRole.MANTENEDOR])
    data = {"is_promotion": is_promotion}
    return await make_ferremas_request(f"/products/{product_id}", "PUT", data)

@app.put("/products/{product_id}/novelty")
async def markAsNovelty(product_id: int, is_novelty: bool, user: User = Depends(get_current_user)):
    """Marcar producto como novedad"""
    check_role_permission(user, [UserRole.ADMIN, UserRole.MANTENEDOR])
    data = {"is_novelty": is_novelty}
    return await make_ferremas_request(f"/products/{product_id}", "PUT", data)

# Endpoints de Sucursales
@app.get("/branches", response_model=List[Sucursal])
async def getBranches(user: User = Depends(get_current_user)):
    """Obtener listado de sucursales"""
    return await make_ferremas_request("/branches")

@app.get("/branches/{branch_id}", response_model=Sucursal)
async def getBranch(branch_id: int, user: User = Depends(get_current_user)):
    """Obtener detalles de una sucursal"""
    return await make_ferremas_request(f"/branches/{branch_id}")

# Endpoints de Vendedores
@app.get("/branches/{branch_id}/sellers", response_model=List[Vendedor])
async def getSellers(branch_id: int, user: User = Depends(get_current_user)):
    """Obtener vendedores por sucursal"""
    return await make_ferremas_request(f"/branches/{branch_id}/sellers")

@app.get("/sellers/{seller_id}", response_model=Vendedor)
async def getSeller(seller_id: int, user: User = Depends(get_current_user)):
    """Obtener vendedor específico"""
    return await make_ferremas_request(f"/sellers/{seller_id}")

@app.get("/sellers/myTeam")
async def getMyTeam(user: User = Depends(get_current_user)):
    """Obtener equipo de vendedores (para jefe de tienda)"""
    check_role_permission(user, [UserRole.JEFE_TIENDA, UserRole.ADMIN])
    return await make_ferremas_request(f"/sellers/team/{user.username}")

# Endpoints de Pedidos
@app.post("/orders")
async def createOrder(order: Order, user: User = Depends(get_current_user)):
    """Crear nuevo pedido"""
    order_data = order.dict()
    order_data["customer"] = user.username
    order_data["created_at"] = datetime.now().isoformat()
    
    return await make_ferremas_request("/orders", "POST", order_data)

# Endpoints de Contacto
@app.post("/contact/seller")
async def contactSeller(contact_request: ContactRequest, user: User = Depends(get_current_user)):
    """Solicitar contacto con vendedor"""
    contact_data = contact_request.dict()
    contact_data["requested_by"] = user.username
    contact_data["created_at"] = datetime.now().isoformat()
    
    # En producción, enviar notificación/email al vendedor
    return {"message": "Solicitud de contacto enviada exitosamente", "contact_id": 12345}

# Endpoints de Pagos (Stripe)
@app.post("/payments/create-payment-intent")
async def createPaymentIntent(payment_request: PaymentRequest, user: User = Depends(get_current_user)):
    """Crear intención de pago con Stripe"""
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment_request.amount * 100),  # Stripe usa centavos
            currency=payment_request.currency,
            payment_method=payment_request.payment_method_id,
            confirmation_method='manual',
            confirm=True,
            receipt_email=payment_request.customer_email
        )
        
        return {
            "client_secret": intent.client_secret,
            "status": intent.status,
            "payment_intent_id": intent.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Error en pago: {str(e)}")

@app.post("/payments/confirm/{payment_intent_id}")
async def confirmPayment(payment_intent_id: str, user: User = Depends(get_current_user)):
    """Confirmar pago con Stripe"""
    try:
        intent = stripe.PaymentIntent.confirm(payment_intent_id)
        return {"status": intent.status, "payment_intent_id": intent.id}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Error confirmando pago: {str(e)}")

# Endpoints de Conversión de Divisas
@app.get("/currency/rates")
async def getCurrencyRates():
    """Obtener tasas de cambio actuales"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BCH_API_URL}/dolar")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error obteniendo tasas de cambio")
        
        data = response.json()
        return {
            "usd_to_clp": data["valor"],
            "clp_to_usd": 1 / data["valor"],
            "date": data["fecha"]
        }

@app.post("/currency/convert")
async def convertCurrency(conversion: CurrencyConversion):
    """Convertir entre CLP y USD"""
    rates = await getCurrencyRates()
    
    if conversion.from_currency.upper() == "CLP" and conversion.to_currency.upper() == "USD":
        converted_amount = conversion.amount * rates["clp_to_usd"]
    elif conversion.from_currency.upper() == "USD" and conversion.to_currency.upper() == "CLP":
        converted_amount = conversion.amount * rates["usd_to_clp"]
    else:
        raise HTTPException(status_code=400, detail="Solo se soporta conversión entre CLP y USD")
    
    return {
        "original_amount": conversion.amount,
        "original_currency": conversion.from_currency.upper(),
        "converted_amount": round(converted_amount, 2),
        "target_currency": conversion.to_currency.upper(),
        "exchange_rate": rates["usd_to_clp"] if conversion.to_currency.upper() == "CLP" else rates["clp_to_usd"]
    }

# Endpoint de salud
@app.get("/health")
async def healthCheck():
    """Verificar estado de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

# Endpoint de información
@app.get("/")
async def root():
    """Información básica de la API"""
    return {
        "message": "FERREMAS Integration API v2.0",
        "documentation": "/docs",
        "health": "/health"
    }
