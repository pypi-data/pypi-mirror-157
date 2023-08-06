(oakprofile) เป็นตัวอย่างการอัพโหลด package ไปยังpypi.org
=========================================================

PyPi: https://pypi.org/project/oakprofile/

สวัสดีครับแพ็คเกจนี้เป็นแพ็คเกจที่อธิบายโปรไฟล์ของนายโอ๊คและสามารถนำไปใช้กับผู้อื่นได้

วิธีติดตั้ง
~~~~~~~~~~~

เปิด CMD / Terminal

.. code:: python

   pip install oakprofile

วิธีใช้งานแพ็คเพจนี้
~~~~~~~~~~~~~~~~~~~~

-  เปิด IDLE ขึ้นมาแล้วพิมพ์…

.. code:: python

   if __name__ == '__main__':
       my= Profile('oak')
       my.company = 'uncle-engineer'
       my.hobby = ['watchingTV' ,'sleeping','reading']
       print(my.name)
       my.show_email()
       my.show_myart()
       my.show_hobby()

พัฒนาโดย: อริญชย์ ชาติละออง
 FB: Arin Chatlaong
