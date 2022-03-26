import config
import smtplib

print(10)
server = smtplib.SMTP('smtp.mail.ru', 465)
server.starttls()

# server.login(sender, config.FROM_EMAIL_PSW)
# server.sendmail(sender,  config.TO_EMAIL, 'Test')
print(0)
server.login('mamsdeveloper@mail.ru', 'UKMBUgvCgWitPf2ydyM3')
print(1)
server.sendmail('mamsdeveloper@mail.ru', config.TO_EMAIL, 'Test')
print(2)
