class Profile:
    '''
    Example :

    my= Profile('oak')
    my.company = 'uncle-engineer'
    my.hobby = ['watchingTV' ,'sleeping','reading']
    print(my.name)
    my.show_email()
    my.show_myart()
    my.show_hobby()
    my.show_hitting()

    '''
    def __init__(self,name) :
        self.name = name
        self.company=''
        self.hobby = []
        self.art=art='''
("`-''-/").___..--''"`-._ 
 `6_ 6  )   `-.  (     ).`-.__.`) 
 (_Y_.)'  ._   )  `._ `. ``-..-' 
   _..`--'_..-_/  /--'_.'
  ((((.-''  ((((.'  (((.-'

        '''

        self.art2= '''
        
        
              _
             | |
             | |===( )   //////
             |_|   |||  | o o|
                    ||| ( c  )                  ____
                     ||| \= /                  ||   \_
                      ||||||                   ||     |
                      ||||||                ...||__/|-"
                      ||||||             __|________|__
                        |||             |______________|
                        |||             || ||      || ||
                        |||             || ||      || ||
------------------------|||-------------||-||------||-||-------
                        |__>            || ||      || ||
        
        
        
        '''
    def show_email(self):
        if self.company !='':
            print('{}@{}.com'.format(self.name.lower(),self.company))
        else:
            print('{}@gmail.com'.format(self.name.lower()))
    
    def show_myart(self):
        print(self.art)
        
    def show_hitting(self):
        print(self.art2)

    def show_hobby(self):
        if len(self.hobby) !=0:
            print('----------my hobby ---------')
            for i,h in enumerate(self.hobby,start=1):
                print(i,h)
            print('---------------')
        else:
            print('No hobby')

if __name__ == '__main__':
    my= Profile('oak')
    my.company = 'uncle-engineer'
    my.hobby = ['watchingTV' ,'sleeping','reading']
    print(my.name)
    my.show_email()
    my.show_myart()
    my.show_hobby()
    my.show_hitting()

#help(my) เพื่อช่วยโดยจะแสดงผลที่คอมเม้นไว้ด้านบน

