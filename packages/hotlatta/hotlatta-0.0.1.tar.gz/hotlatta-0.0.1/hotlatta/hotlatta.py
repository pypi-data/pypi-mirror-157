from cgitb import text
import webbrowser

class HotLatta:
    """
    # กาแฟลาเต้ร้อนคืออะไร
    # วิธีการทำลาเต้ร้อน
    # ส่วนผสมของลาเต้ร้อน
    # โชว์วิธีการทำ
    # โชว์วิธีทำ youtube
    # โชว์รูปภาพ

    Example:
    # ----------------------------
    latta = HotLatta()
    latta.what_is_it()
    latta.show_ingredients()
    latta.show_how_to(eng=True)
    latta.show_youtube()
    latta.show_ascii()
    # ----------------------------
    """
    def __init__(self):
        self.youtubeurl = 'https://www.youtube.com/watch?v=nyfEGWzmHTg'
        self.youtubeurl_eng = 'https://www.youtube.com/watch?v=aUux07XtrYg'

    def what_is_it(self):
        '''
        # ลาเต้ร้อนคืออะไร
        '''
        text = '''
        เป็นภาษาอิตาลีแปลว่านม ส่วนในประเทศอื่น จะหมายถึงกาแฟลาเต้หรือเครื่องดื่อมกาแฟที่เตรียม
        ด้วยนมสตึมร้อน

        ref: The Old School : Specialty Coffee & Patisserie
        '''
        print(text)
       
    def show_ingredients(self,eng=False):
        '''
        # ส่วนผสม
        '''
        text = '''
        น้ำกาแฟ (เอสเพลสโซ่ช็อต) 1oz (30ml)
        นมสดเกือบเต็มแก้ว
        ฟองนม
        '''
        text_eng = '''
        Espresso
        Whipped milk
        Milk foam
        '''
        if eng == True:
            print(text_eng)
        else:
            print(text)

    def show_how_to(self,eng=False):
        '''
        # วิธีการทำ
        '''
        text = '''
        - กดช็อตเอสเพรสโซ่ใส่แก้ว 1 oz
        - เทนมร้อนใส่แก้ว เกือบเต็มแก้ว
        - ตักฟองนมท็อปด้านบน
        - ตกแต่งให้เป็นลาเต้อาร์ทตามชอบ
        '''
        text_eng = '''
        - Brew the coffee or espresso of your choice
        - While the coffee is brewing, heat the milk of your choice for 30-45 seconds in a microwave-safe coffee mug
        - Once the milk is heated, take a small whisk and vigorously whisk back and forth for 15-30 seconds until the milk is frothy
        - Pour the coffee into a mug. GENTLY, pour the frothed milk on top of the coffee
        - The foam will rise to the top of the mug, giving you a pretty close replication of a traditional latte
        '''
        if eng == True:
            print(text_eng)
        else:
            print(text)
    
    def show_youtube(self,eng=False,open=False):
        '''
        # คลิปวิธีการทำ
        '''
        if eng == True:
            print(self.youtubeurl_eng)
            if open == True:
                webbrowser.open(self.youtubeurl_eng)

        else:
            print(self.youtubeurl)
            if open == True:
                webbrowser.open(self.youtubeurl)

    def show_ascii(self):
        text='''
                            )  (
                        (   ) )
                        ) ( (
                    mrf_______)_
                    .-'---------|  
                    ( C|/\/\/\/\/|
                    '-./\/\/\/\/|
                    '_________'
                        '-------'
            '''
        print(text)

if __name__ == '__main__':
    latta = HotLatta()
    latta.what_is_it()
    latta.show_ingredients()
    latta.show_how_to(eng=True)
    latta.show_youtube()
    latta.show_ascii()