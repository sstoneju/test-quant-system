import traceback


def main():
    try:
        print("This program converts a temperature from Celsius to Fahrenheit.")
        print()

        celsius = eval(input("What is the Celsius temperature? "))
        fahrenheit = 9/5 * celsius + 32

        print("The temperature is", fahrenheit, "degrees Fahrenheit.")
    except Exception as e:
        print(e)
        print(traceback.format_exc())