เป็นแพ็คเกจ Python เกี่ยวกับการทำกาแฟลาเต้
==========================================

PyPi: https://pypi.org/project/hotlatta/

สวัสดีค่ะ แพ็คเกจนี้เกี่ยวกับการทำกาแฟลาเต้ร้อน
สามารถดาวน์โหลดและเข้าไปดูวิธีทำได้

วิธีติดตั้ง
~~~~~~~~~~~

เปิด CMD / Terminal

.. code:: python

   pip install hotlatta

วิธีใช้งานแพ็คเพจนี้
~~~~~~~~~~~~~~~~~~~~

-  เปิด IDLE ขึ้นมาแล้วพิมพ์…

.. code:: python

   from hotlatta import HotLatta

   latta = HotLatta() #ประกาศชื่อ class
   latta.what_is_it() 
   latta.show_ingredients()
   latta.show_how_to(eng=True)
   latta.show_youtube()
   latta.show_ascii()
