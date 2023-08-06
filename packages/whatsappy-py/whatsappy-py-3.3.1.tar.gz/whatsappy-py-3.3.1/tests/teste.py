from whatsappy import Whatsapp
from rich.console import Console

whatsapp = Whatsapp()
console = Console()

whatsapp.login(visible=True)

group = whatsapp.chat("Console")
console.print(group)

contacts = whatsapp.contact_list
console.print(contacts)

input()

whatsapp.close()
