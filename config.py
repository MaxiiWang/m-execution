class Config:
    DB_TYPE = "iDOP"
    DB_NAME = "app"
    
    DFOps_SERVER_URL = "https://idfops-gateway.data4industry.com:30843/"

    ORDER_BUSINESS_STAGE = {
        "quote": "报价",
        "contract": "签单",
        "partially_paid": "部分付款",
        "fully_paid": "全额付款",
    }

    APP_ID = 'ea3574a4062f4e15af9fe31a1e6add79'

    TENANT_ID = 'Default'