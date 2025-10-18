from api.api import app
from loader import db
import asyncio
import ssl


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='ssl/cert.pem', keyfile='ssl/pk.pem')
    asyncio.run(db.create_db())
    app.run(host='', port=443, debug=True, ssl_context=context)
