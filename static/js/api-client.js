// API Client para Ferremas
// Archivo: static/js/api-client.js

class FerremasAPI {
    constructor() {
        this.baseURL = 'http://localhost';
        this.productosPort = '5000';
        this.divisasPort = '5001';
    }

    // Función para consultar stock via API
    async consultarStockAPI(codigo) {
        try {
            const response = await fetch(`${this.baseURL}:${this.productosPort}/api/productos/${codigo}/stock`);
            const data = await response.json();

            if (response.ok) {
                this.mostrarModalStock(data);
            } else {
                this.mostrarError(`Error: ${data.error}`);
            }
        } catch (error) {
            this.mostrarError('Error de conexión con la API de productos');
            console.error('Error:', error);
        }
    }

    // Función para obtener información de divisas
    async obtenerDivisas() {
        try {
            const response = await fetch(`${this.baseURL}:${this.divisasPort}/api/divisas/usd-clp`);
            const data = await response.json();

            if (response.ok) {
                return data;
            } else {
                console.error('Error obteniendo divisas:', data.error);
                return null;
            }
        } catch (error) {
            console.error('Error de conexión con API de divisas:', error);
            return null;
        }
    }

    // Función para agregar producto via API
    async agregarProductoAPI(formData) {
        try {
            const response = await fetch(`${this.baseURL}:${this.productosPort}/api/productos`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                this.mostrarExito('Producto agregado exitosamente via API');
                setTimeout(() => {
                    window.location.href = '/catalog';
                }, 2000);
            } else {
                this.mostrarError(`Error: ${data.error}`);
            }
        } catch (error) {
            this.mostrarError('Error de conexión con la API');
            console.error('Error:', error);
        }
    }

    // Función para obtener todos los productos via API
    async obtenerProductos() {
        try {
            const response = await fetch(`${this.baseURL}:${this.productosPort}/api/productos`);
            const data = await response.json();

            if (response.ok) {
                return data;
            } else {
                console.error('Error obteniendo productos:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error de conexión con API de productos:', error);
            return [];
        }
    }

    // Mostrar modal con información de stock
    mostrarModalStock(data) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>📊 Consulta de Stock via API</h3>
                    <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">&times;</button>
                </div>
                <div class="modal-body">
                    <p><strong>Código:</strong> ${data.codigo}</p>
                    <p><strong>Stock disponible:</strong> ${data.stock} unidades</p>
                    <p><strong>Fuente:</strong> API REST Ferremas</p>
                    <p><strong>Endpoint:</strong> GET /api/productos/${data.codigo}/stock</p>
                    <hr>
                    <small>Esta información fue obtenida mediante nuestra API REST</small>
                </div>
                <div class="modal-footer">
                    <button onclick="this.closest('.modal-overlay').remove()" class="btn-primary">Cerrar</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    // Mostrar mensaje de éxito
    mostrarExito(mensaje) {
        this.mostrarNotificacion(mensaje, 'success');
    }

    // Mostrar mensaje de error
    mostrarError(mensaje) {
        this.mostrarNotificacion(mensaje, 'error');
    }

    // Sistema de notificaciones
    mostrarNotificacion(mensaje, tipo) {
        const notification = document.createElement('div');
        notification.className = `notification ${tipo}`;
        notification.innerHTML = `
            <span>${mensaje}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // Actualizar precios en tiempo real
    async actualizarPreciosUSD() {
        const divisas = await this.obtenerDivisas();
        if (divisas) {
            const preciosUSD = document.querySelectorAll('.precio-usd');
            const preciosCLP = document.querySelectorAll('.precio-clp');

            preciosCLP.forEach((elementoCLP, index) => {
                const precioCLP = parseFloat(elementoCLP.textContent.replace(/[^0-9]/g, ''));
                const precioUSD = Math.round((precioCLP / divisas.tipo_cambio) * 100) / 100;

                if (preciosUSD[index]) {
                    preciosUSD[index].textContent = `$${precioUSD} USD`;
                }
            });
        }
    }
}

// Instancia global de la API
const ferremasAPI = new FerremasAPI();

// Funciones globales para compatibilidad
function consultarStockAPI(codigo) {
    ferremasAPI.consultarStockAPI(codigo);
}

function agregarProductoViaAPI() {
    const form = document.getElementById('form-producto');
    if (form) {
        const formData = new FormData(form);
        const data = {
            codigo: formData.get('codigo'),
            nombre: formData.get('nombre'),
            valor: parseInt(formData.get('valor')),
            stock: parseInt(formData.get('stock')),
            imagen: formData.get('imagen'),
            descripcion: formData.get('descripcion') || ''
        };
        ferremasAPI.agregarProductoAPI(data);
    }
}

// Inicializar cuando la página cargue
document.addEventListener('DOMContentLoaded', function() {
    // Actualizar precios USD si estamos en el catálogo
    if (window.location.pathname === '/catalog') {
        ferremasAPI.actualizarPreciosUSD();
    }

    console.log('🚀 Ferremas API Client inicializado');
});
