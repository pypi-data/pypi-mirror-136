from whatsappy import Whatsapp
from rich.console import Console

whatsapp = Whatsapp()
console = Console()

whatsapp.login(visible=True)

group = whatsapp.chat("manda foto de fuzil")
group = whatsapp.chat("__Python__Iniciantes")

whatsapp.close()

