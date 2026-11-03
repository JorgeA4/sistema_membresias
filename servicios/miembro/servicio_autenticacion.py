from clases.miembro import Miembro
import base_de_datos.consultas as bd

def autenticar_miembro(correo: str, contraseña: str) -> Miembro | None:
    miembro = bd.buscar_miembro_por_correo(correo)
    if miembro and miembro.contraseña == contraseña:
        return miembro
    else:
        return None

def eliminar(lista, num): # 'num' es la clave del elemento
    #Diccionario de datos
    if isinstance(lista, dict):
        if num in lista:
            del lista[num]
            print(f"El elemento '{num}' fue eliminado exitosamente")
        else:
            print(f"El elemento '{num}' no existe")

    #Lista de datos
    elif isinstance(lista, list): # num puede tratarse de la 'id' dentro de la lista
        for i in lista:
            if getattr(i, 'id', None) == num:
                lista.remove(num)
                print(f"El elemento con la ID {num} ha sido eliminado exitosamente")
        print(f"El elemento con la ID {num} no se encuentra")
    else: 
        print("El tipo de lista no es compatible")

def modificar(elemento, atributo: str, nuevo_valor): # atributo es para definir el tipo de variable
    if hasattr(elemento, atributo):
        setattr(elemento, atributo, nuevo_valor)
        print(f"El elemento '{atributo}' ahora es '{nuevo_valor}'")
    else:
        print(f"El elemento'{atributo}' no existe en este objeto")
