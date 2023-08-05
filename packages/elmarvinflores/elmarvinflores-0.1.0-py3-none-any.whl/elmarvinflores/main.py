def es_primo(numero):
    """Valida si numero es primo"""
    respuesta = True
    
    for divisor in range(2, numero):
        es_divisible = numero % divisor == 0
        if es_divisible:
            respuesta = False
            break
        
    return respuesta

def primos(a, b):
    """Obtiene una lista de números primos en el intervalo de 'a' a 'b'"""
    return list(filter(es_primo, range(a, b)))

def main():
    """Método principal"""
    print('Cálculo de números primos')
    limite_inferior = int(input("Ingrese el límite inferior: "))
    limite_superior = int(input("Ingrese el límite superior: "))
    
    resultado = primos(limite_inferior, limite_superior)
    print(f"Todos los números primos que hay entre {limite_inferior} y {limite_superior}")
    print(",".join(map(str, resultado)))
    
if __name__ == '__main__':
    main()
