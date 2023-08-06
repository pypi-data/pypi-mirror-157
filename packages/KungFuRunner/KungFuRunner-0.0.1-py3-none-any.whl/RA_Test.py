import os
import datetime
import unittest
 from dataclasses import dataclass
 
@dataclass(order=True, frozen=True)
class DatedNote:
    #def __init__(self, 
    date: datetime.datetime
    note: str
    
    # Method on class

    
    # Additional logic in main `run` function.


 
class test_NoteWriter(unittest.TestCase):


class NoteWriter:
    '''
    We have this great utility as follows:
    
    Example Usage:
    ​
        $ python note_cli.py
        > I want to make a note
        > And then another note
        > Then, look at my history
        > h
        2021-05-07 16:44; I want to make a note
        2021-05-07 16:44; And then another note
        2021-05-07 16:45; Then, look at my history
    
        > Then, clear my notes
        > c
        Are you sure? (y/n): y
        Cleared!
        > Then, quit.
        > h
        2021-05-07 16:46; Then, quit.
    
        > q
        ​
        $ python note_cli.py
        > But my notes persist.
        > h 2
        2021-05-07 16:46; Then, quit.
        2021-05-07 16:52; But my notes persist.
    
        > q
    '''
    def __init__(self):
        self.note_file = '/tmp/note_cli_store.txt'
        self.notes = []
        self.default_note_count = 10
        self.current_mode = 'F'
    
    def set_up(self):
        if os.path.exists(self.note_file):
            with open(self.note_file, 'r') as f:
                for line in f.readlines():
                    self.notes.append(line)
                    #self.notes = [n.rstrip('\n') for n in list(f.readlines())]
    
    def tear_down(self):
        with open(self.note_file, 'w+') as f:
            for note in self.notes:
                f.write(note + '\n')
    
    def write_note(self, note):
        self.notes.append(note)
    
    def clear_all_notes(self):
        self.notes.clear()
    
    def display_previous(self, n):
        for note in self.notes[-n:]:
            print(note)

    def display_range(self, date_from=None, date_to=None):
        dns = {}
        
        for i, note in enumerate(self.notes):
            try:
                timestamp, *note_body = note.split(';')
                note_body = ' '.join(note_body)
                timestamp = datetime.datetime.strptime(timestamp, r'%Y-%m-%d %H:%M')
                dn = self.DatedNote(timestamp, note_body) # Strip semicolon
                dns[i] = dn
            except:
                break
                #continue?
        
        if date_from == None or date_to == None:
            date_from = datetime.datetime.min
            date_to = datetime.datetime.max
        else:
            try:
                date_from = datetime.datetime.fromisoformat(date_from) if date_from is not None else datetime.datetime.min
                date_to = datetime.datetime.fromisoformat(date_to) if date_to is not None else datetime.datetime.max
            except:
                print('date format error!')
        
        for i, dn in sorted(dns.items(), key=lambda item: item[1]):
            if dn.date > date_from or dn.date < date_to:
                print(self.notes[i])
    
    def run(self) -> bool:
        '''
        Returns whether or not the session is over and we are waiting for more input from the user.
        '''

        try:
            while True:
                user_input = input('> ')
                # Do nothing if no input
                if not user_input:
                    continue
                if self.Mode = 'F':

                    if user_input.upper() in ['W:', '']:
                        self.Mode = 'W:'


                    if user_input.upper() in ['Q', 'QUIT', 'EXIT']:
                        break
                
                    if user_input.upper() in ['H', 'HISTORY']:
                        if len(user_input.upper().split()) == 2:
                            #num_notes = eval(user_input.upper().split()[1])
                            num_notes = int(user_input.upper().split()[1])
                        else:
                            num_notes = self.default_note_count
                
                        self.display_previous(num_notes)
                        continue
                
                    if user_input.upper() in ['C', 'CLEAR']:
                        if input('Are you sure? (y/n): ') == 'y':
                            self.clear_all_notes()
                            print('Cleared!')
                            continue
                    try:
                        if user_input.upper().split()[0] == 'FR':
                            self.display_range(*user_input.split()[1:])
                            print()
                            continue
                        
                        if user_input.upper().split()[:2] == ['FILTER', 'RANGE']:
                            self.display_range(*user_input.split()[2:])
                            print()
                            continue

                    except TypeError as e:
                        print('Filter Range takes two arguments max: [date from] [date to]')
                        continue
                if self.Mode = 'W:':
                    
                now = datetime.datetime.now().strftime(r'%Y-%m-%d %H:%M')
                self.write_note('{now}; {user_input}'.format(now=now, user_input=user_input))
                continue
        
        except KeyboardInterrupt:
            return

        finally:
            self.tear_down()


def main():
    app = NoteWriter()
    app.set_up()
    app.run()

if __name__ == '__main__':
    main()
