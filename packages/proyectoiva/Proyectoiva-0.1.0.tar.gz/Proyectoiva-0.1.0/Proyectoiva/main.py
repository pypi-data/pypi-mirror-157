from Proyectoiva.mensajes.saludo import bienvenida, despedida

def main():
	nombre = input("¿Cuál es tú nombre?")
	print(bienvenida(nombre))

if __name__ == '__main__':
	main()