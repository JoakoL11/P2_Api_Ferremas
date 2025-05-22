# FERREMAS API de Integración v2.0

API REST para la integración de servicios de FERREMAS, incluyendo gestión de productos, procesamiento de pagos y conversión de divisas.

## 🚀 Características

- ✅ **Autenticación segura** con Bearer Tokens
- ✅ **RBAC** (Control de Acceso Basado en Roles)
- ✅ **Integración con Stripe** para pagos
- ✅ **Conversión de divisas** CLP ↔ USD
- ✅ **Gestión completa** de productos y sucursales
- ✅ **Documentación automática** con OpenAPI
- ✅ **Despliegue en Railway** con HTTPS

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Python 3.11** - Lenguaje de programación
- **Railway** - Plataforma de despliegue
- **Stripe API** - Procesamiento de pagos
- **Banco Central API** - Conversión de divisas


## 🚀 Instalación y Despliegue

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/ferremas-api.git
cd ferremas-api
```

### 2. Instalar dependencias localmente
```bash
pip install -r requirements.txt
```

### 3. Ejecutar localmente
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuración


## 📚 Documentación

Una vez desplegado, accede a:
- **Swagger UI**: `https://tu-api.railway.app/docs`
- **ReDoc**: `https://tu-api.railway.app/redoc`
- **Health Check**: `https://tu-api.railway.app/health`

## 🔐 Autenticación


## 🛡️ Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **Admin** | Acceso completo |
| **Mantenedor** | Gestión de productos |
| **Jefe Tienda** | Ver equipo, inventario |
| **Cliente** | Consultas, pedidos |

## 📡 Endpoints Principales

### Productos
- `GET /products/catalog` - Catálogo completo
- `GET /products/promotions` - Productos en promoción
- `POST /products` - Agregar producto (Admin/Mantenedor)

### Sucursales
- `GET /branches` - Listado de sucursales
- `GET /branches/{id}/sellers` - Vendedores por sucursal

### Pagos
- `POST /payments/create-payment-intent` - Crear pago con Stripe
- `POST /payments/confirm/{id}` - Confirmar pago

### Divisas
- `GET /currency/rates` - Tasas actuales CLP/USD
- `POST /currency/convert` - Convertir divisas

## 🧪 Pruebas


## 📁 Estructura del Proyecto

```
ferremas-api/
├── main.py              # API principal
├── requirements.txt     # Dependencias
├── README.md           # Este archivo
├── .gitignore          # Archivos ignorados
```

## 🚨 Casos de Uso Implementados

- ✅ **Como cliente**: Consultar sucursales y productos en promoción
- ✅ **Como mantenedor**: Agregar productos al catálogo
- ✅ **Como jefe de tienda**: Ver equipo de vendedores
- ✅ **Como cliente**: Realizar compra con Stripe

## 🔍 Monitoreo

Railway proporciona:
- Logs en tiempo real
- Métricas de rendimiento
- Health checks automáticos
- Alertas de errores

## 👥 Equipo de Desarrollo

- **Jefe de Proyecto**: [Tu nombre]
- **Desarrollador Backend**: [Tu nombre]
- **Arquitecto de Software**: [Tu nombre]

## 📝 License

Este proyecto es parte de la evaluación académica de Integración de Plataformas.

---

## 🆘 Soporte

Para problemas o consultas:
1. Revisar la documentación en `/docs`
2. Verificar logs con `railway logs`
3. Contactar al equipo de desarrollo
