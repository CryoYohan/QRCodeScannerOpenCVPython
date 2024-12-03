import segno

class QRMaker:
    def create_qr(self, data:str):
        # Create QR from data:str which is student IDNO
        qrcode = segno.make_qr(data)
        qrcode.save(
            f"static/images/studentimage/{data}.png",
            scale=5,
            border=0
            )