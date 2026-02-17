# Integrated Supply Chain Management and Logistics System (Backend)

This repository contains the backend implementation for a senior project focused on designing an **Integrated Supply Chain Management and Logistics System** for B2B operations within Ethiopian cities.

## Project Overview

The system aims to improve visibility, coordination, and efficiency across procurement, warehouse operations, and delivery processes. It addresses challenges such as manual order handling, limited delivery tracking, and fragmented procurement workflows.

**Key Features:**
*   **Procurement Automation:** Management of RFQs (Request for Quotations) and supplier quotations.
*   **Warehouse Operations:** Centralized order and inventory management with QR-coded package tracking.
*   **Delivery Management:** Directed driver workflow for accepting delivery requests and updating status (supports GPS tracking integration).
*   **Role-Based Access Control:** Distinct interfaces and permissions for Admins, Sales Staff, Warehouse Staff, Suppliers, and Drivers.
*   **Dashboard & Analytics:** Centralized oversight for operational metrics.

**Note:** This system is designed as an academic senior project foundation. Advanced analytics and deep security features were intentionally scoped out to fit the project timeline.

## Tech Stack

*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
*   **Database:** PostgreSQL (via [Supabase](https://supabase.com/))
*   **IRM/ORM:** [SQLModel](https://sqlmodel.tiangolo.com/) / SQLAlchemy
*   **Authentication:** JWT (JSON Web Tokens)
*   **Architecture:** MVC-style with modular routing

## Project Structure

```bash
supply/
├── main.py                 # Application entry point and router configuration
├── db.py                   # Database connection and session management
├── auth.py                 # Authentication middleware and utilities
├── model/                  # SQLModel database models (Data Layer)
│   ├── delivery.py
│   ├── orders.py
│   ├── product.py
│   └── ...
├── routes/                 # API Endpoints (Controller Layer)
│   ├── admin_route.py
│   ├── procurement_route.py
│   ├── warehouse_route.py
│   └── ...
└── requirements.txt        # Project dependencies
```

## Setup & Installation

### Prerequisites
*   Python 3.9+
*   PostgreSQL database (or a Supabase project)

### 1. Clone the Repository
```bash
git clone https://github.com/EtsubFikreab/supply.git
cd supply
```

### 2. Install Dependencies
Create a virtual environment (recommended) and install the requirements.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add the following configurations (based on your Supabase/PostgreSQL setup):

```ini
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret
POSTGRES=postgresql://user:password@host:port/database
```

### 4. Run the Application
You can run the server using `uvicorn` or the FastAPI CLI.

```bash
fastapi dev main.py
# OR
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

FastAPI provides automatic interactive documentation. Once the server is running, visit:

*   **Swagger UI:** `http://127.0.0.1:8000/docs`
*   **ReDoc:** `http://127.0.0.1:8000/redoc`

## Future Work

This project provides a modular foundation that can be extended with:
*   Real-time route optimization for drivers.
*   Advanced demand forecasting and analytics.
*   Integration with external financial/ERP systems.
*   Enhanced security auditing and compliance features.

## License

This project is for academic purposes.
