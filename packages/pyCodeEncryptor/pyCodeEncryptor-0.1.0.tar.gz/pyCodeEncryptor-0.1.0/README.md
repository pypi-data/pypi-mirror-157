# pyCodeEncryptor
pyCodeEncryptor, python için yazılmış bir kod şifreleme kütüphanesidir.

Kullanımı oldukça basittir.

**Fonksiyonlar**

 - encrypt
 - runCode

## encrypt
Kodun şifrelenmesine yarar.

### PARAMETRELER
 1. file
 2. out

***Örnek Kullanım:***

**program .py**

    from colorama import init,Fore,Back
    init(autoreset=True)
    name=input("What is your name: ")
    print(Back.YELLOW+Fore.RED+f"Hello, {name}")

**şifrele .py**

    import pyCodeEncryptor
    pyCodeEncryptor.encrypt("program.py","şifreliProgram.txt")


şifrele .py dosyasını çalıştıracak olursak sonucunda çıkan şifreliProgram .txt dosyasında program.py dosyasının şifreli halini bulabiliriz.

**şifreliProgram .txt**(İÇERİK SÜRÜME GÖRE FARKLILIK GÖSTEREBİLİR)

    ğşpo%dpnpşcoc%kospşt%kökt,Fpşg,Bcdm&kökt"cvtpşgugt?Tşvg=&öcog?kösvt"~Wict%ku%apvş%öcog
    %~=&sşköt"Bcdm.YELLOW+Fpşg.RED+ğ~Hgnnp,%{öcog}~=


## runCode

Şifreli kodu çalıştırmaya yarar.

### PARAMETRELER
 1. code


***Örnek Kullanım:***

    from pyCodeEncryptor import runCode
    code='ğşpo%dpnpşcoc%kospşt%kökt,Fpşg,Bcdm&kökt"cvtpşgugt?Tşvg=&öcog?kösvt"~Wict%ku%apvş%öcog\n%~=&sşköt"Bcdm.YELLOW+Fpşg.RED+ğ~Hgnnp,%{öcog}~='
    runCode(code)


## Şifrelenmiş programı .exe dosyasına dönüştürmek(pyinstaller)

pyinstaller modülünü indirip kurduktan sonra isteğimize göre pyinstaller kodunu terminale yazıyoruz(kullanım: [PYINSTALLER DOCUMENTATION](https://pyinstaller.org/en/stable/)).

Terminal kodunu istediğimz şekilde yazdıktan şu eklemeleri yapıyoruz

pyinstaller ~~--onefile --noconsole~~ --hidden-import MODUL1 --hidden-import MODUL2 ~~program.py~~
(Özelleştirilecek kısımlar üstü çizili bir şekilde yazılmıştır.)

MODUL1 ve MODUL2(ihtiyaca göre --hidden-import parametresi ile çoğaltılabilir veya azaltılabilir.) kısımlarına programda kullanılan modül isimleri yazılacaktır(pyCodeEncryptor hariç). Bu düzeltme yapıldıktan sonra kod çalıştırılarak .exe dosyasına ulaşılabilinir.


[WWW.MAMOSKO.ML](https://mamosko.ml)
[admin@mamoskomail.ml](mailto:admin@mamoskomail.ml)