import miniparser
import csv
import configparser
import sys
import os
import shutil
from pathlib import Path

if sys.platform.startswith('linux'):
    files_path = os.path.expanduser('~/.n')
elif sys.platform.startswith('win32'):
    files_path = os.path.expanduser('~/.n')
elif sys.platform.startswith('darwin'):
    files_path = os.path.expanduser('~/.n')
else:
    files_path = os.path.expanduser('~/.n')

class NotebookCollection:
    def __init__(self):

        self.notebooks = {} # will be overwritten, but init needed

        self.notebooks_path = os.path.join(files_path, 'notebooks')
        self.notebooks_file_path = os.path.join(files_path, 'notebooks.txt')
        # if doesn't exist, create it & copy base settings
        if not os.path.exists(self.notebooks_path):
            defaults_source_path = Path(__file__).parent.resolve()
            os.makedirs(self.notebooks_path)
            shutil.copy2(os.path.join(defaults_source_path, 'defaults', 'settings.ini'), files_path)
            shutil.copy2(os.path.join(defaults_source_path, 'defaults', 'notebooks.txt'), files_path)
            self.create_notebook('main')

        if os.path.exists(os.path.join(files_path, 'settings.ini')):
            self.config = configparser.ConfigParser()
            self.settings_path = os.path.join(files_path, 'settings.ini')
            self.config.read(self.settings_path)

        # for custom path notebooks (if custom path specified in settings.ini)
        if not self.config['main']['custom_notebooks_path'] == '':
            self.notebooks_path = os.path.expanduser(self.config['main']['custom_notebooks_path'])

        self.active_notebook_name = self.config['main']['active_notebook']
        # is no active notebook set in settings, first notebook is the active one
        if self.active_notebook_name == '':
            self.load_notebooks()
            if self.notebooks == {}:
                nb_name = input('No existing notebook. Choose notebook name: ')
                self.active_notebook_name = nb_name
            else:
                first_notebook = list(self.notebooks.keys())[0]
                self.active_notebook_name = first_notebook
        # try / except in case no file for active notebook exists
        try:
            self.active_notebook = Notebook(
                self.active_notebook_name,
                self.get_notebook_path(self.active_notebook_name)
                )
        except:
            self.create_notebook(self.active_notebook_name)
            self.active_notebook = Notebook(
                self.active_notebook_name,
                self.get_notebook_path(self.active_notebook_name)
                )
        self.load_notebooks()

    def set_custom_notebooks_path(self, new_path):
        new_path_expanded = os.path.expanduser(new_path)
        self.config['main']['custom_notebooks_path'] = new_path_expanded
        self.save_config()
        print(f"'{new_path_expanded}' : new notebooks path")

    def get_custom_notebooks_path(self):
        if self.config['main']['custom_notebooks_path'] == '':
            print(self.notebooks_path)
        else:
            print(self.config['main']['custom_notebooks_path'])

    def get_notebook_path(self, notebook_name):
        with open(self.notebooks_file_path, 'r') as f:
            notebooks_data = list(csv.reader(f))
            self.notebooks = {}
            for nb in notebooks_data[1:]:
                nb_name, nb_path = nb[0], nb[1]
                if notebook_name == nb_name:
                    return nb_path
            print(f"No notebook named '{notebook_name}'")

    def load_notebooks(self):
        with open(self.notebooks_file_path, 'r') as f:
            notebooks_data = list(csv.reader(f))
            self.notebooks = {}
            for nb in notebooks_data[1:]:
                nb_name = nb[0]
                nb_path = nb[1]
                self.notebooks[nb_name] = Notebook(nb_name, nb_path)

    def save_config(self):
        with open(self.settings_path, 'w') as configfile:
            self.config.write(configfile)

    def get_active_notebook(self):
        print(f"Active notebook: {self.active_notebook.name}")

    def set_active_notebook(self, notebook):
        if notebook.startswith('@'):
            notebook = notebook[1:]
        if notebook in self.notebooks:
            self.config['main']['active_notebook'] = notebook
            self.save_config()
            print(f"'{notebook}' active notebook!")
        else:
            print(f"Notebook '{notebook}' doesn't exist.")

    def list_notebooks(self, *args):
        if args:
            if args[0] == 'path':
                print('Notebooks:')
                for nb in self.notebooks:
                    nb_path = self.get_notebook_path(nb)
                    if self.active_notebook_name == nb:
                        print(f'- {nb} [active notebook], {nb_path}')
                    else:
                        print(f'- {nb}, {nb_path}')
        else:
            print('Notebooks:')
            for nb in self.notebooks:
                if self.active_notebook_name == nb:
                    print(f'- {nb} [active notebook]')
                else:
                    print(f'- {nb}')

    def ls_cmd(self, *args):
        if self.notebook_option_check(*args):
            notebook, args_rest = self.notebook_option_args(*args)
            if notebook in self.notebooks:
                self.notebooks[notebook].view_notes(*args_rest)
            else:
                print(f"Notebook '{notebook}' doesn't exist.")
        else:
            self.active_notebook.view_notes(*args)
    
    def notebook_option_check(self, *args):
        try:
            if args[0].startswith('@'):
                return True
            else:
                return False
        except:
            return False

    def notebook_option_args(self, *args):
            notebook = args[0][1:] # get notebook name
            args_rest = args[1:] # get rest of command arguments
            return notebook, args_rest

    def add_cmd(self, *args):
        if self.notebook_option_check(*args):
            notebook, args_rest = self.notebook_option_args(*args)
            # add note to specified notebook @<notebook>
            if notebook in self.notebooks:
                self.notebooks[notebook].add(*args_rest)
            # create notebook:
            elif args_rest == ():
                create_nb_prompt = input(f"Notebook '{notebook}' doesn't exist. Create it, y/n? ")
                if create_nb_prompt in ('y', 'yes', 'Y'):
                    self.create_notebook(notebook)
            # create notebook and add note
            else:
                create_nb_prompt = input(f"Notebook '{notebook}' doesn't exist. Create it and add note: '{' '.join(args_rest)}', y/n? ")
                if create_nb_prompt in ('y', 'yes', 'Y'):
                    self.create_notebook(notebook)
                    self.notebooks[notebook].add(*args_rest)
        # add note to default / active notebook
        else:
            self.active_notebook.add(*args)

    def delete_notebook(self, notebook):
        if notebook in self.notebooks:
            del_prompt = input(f"Do you really want to delete notebook '{notebook}', y/n? ")
            if del_prompt in ('y', 'yes', 'Y'):
                # delete notebook file:
                os.remove(self.notebooks[notebook].path)
                # delete notebook entry in notebooks.txt list:
                with open(self.notebooks_file_path, 'r') as f:
                    file_content = list(csv.reader(f))
                    header = file_content[0]
                    notebooks_list = file_content[1:]
                    notebooks_list_new = [
                        nb for nb in notebooks_list if notebook != nb[0]
                    ]
                with open(self.notebooks_file_path, 'w') as f:
                    write = csv.writer(f)
                    write.writerow(header)
                    write.writerows(notebooks_list_new)
                # if notebook was active, remove it from being active:
                if self.active_notebook_name == notebook:
                    self.load_notebooks()
                    # create new main active notebook
                    if self.notebooks == {}:
                        self.config['main']['active_notebook'] = ''
                        self.save_config()
                        print(f"No more active notebook!")
                    # set new active notebook
                    else:
                        first_notebook = list(self.notebooks.keys())[0]
                        # self.active_notebook_name = first_notebook
                        self.config['main']['active_notebook'] = first_notebook
                        self.save_config()
                        print(f"'{first_notebook}' new active notebook!")
                print(f"Notebook '{notebook}' deleted!")
        else:
            print(f"Can't delete notebook. Notebook '{notebook}' doesn't exist.")

    def delete_notes_or_notebook_cmd(self, *args):
        # delete notebook
        if len(args) == 1 and args[0].startswith('@'):
            notebook = args[0][1:]
            self.delete_notebook(notebook)
        # delete notes:
        else:
            if self.notebook_option_check(*args):
                notebook, args_rest = self.notebook_option_args(*args)
                if notebook in self.notebooks:
                    self.notebooks[notebook].delete_notes(*args_rest)
                else:
                    print(f"Delete note(s) cancelled. No notebook named '{notebook}'.")
            else:
                self.active_notebook.delete_notes(*args)

    def delete_notes_range_cmd(self, *args):
        if self.notebook_option_check(*args):
            notebook, args_rest = self.notebook_option_args(*args)
            if notebook in self.notebooks:
                self.notebooks[notebook].delete_notes_range(*args_rest)
            else:
                print(f"Delete notes cancelled. No notebook named '{notebook}'.")
        else:
            args = args[:-1]
            self.active_notebook.delete_notes_range(*args)

    def create_notebook(self, notebook_name):
        if notebook_name in self.notebooks:
            print('Notebook with the same name already exists!')
        else:
            # prompt user if sure to create notebook?
            file_name = notebook_name + '.md'
            file_path = os.path.join(self.notebooks_path, file_name)
            try:
                with open(file_path, 'w') as nb_file:
                    nb_file.write(f'# {notebook_name}\n')
            # create notebooks dir if it doesn't exist:
            except:
                os.makedirs(self.notebooks_path)
                with open(file_path, 'w') as nb_file:
                    nb_file.write(f'# {notebook_name}\n')
            with open(self.notebooks_file_path, 'r') as notebooks_file:
                nb_files_content= notebooks_file.read()
            with open(self.notebooks_file_path, 'a') as notebooks_file:
                if not nb_files_content.endswith('\n'):
                    notebooks_file.write('\n')
                notebooks_file.write(f'{notebook_name},{file_path}\n')
            self.load_notebooks()
            print(f'Notebook {notebook_name} created!')

class Notebook:
    def __init__(self,name,path):
        self.name = name
        self.path = path
        self.notes: list = self.load()

    def load(self) -> list:
        with open(self.path, 'r') as notebook_file:
            notes = notebook_file.readlines()[1:]
        return notes

    def save(self):
        with open(self.path, 'r') as notebook_file:
            first_line = notebook_file.readlines()[0]
        with open(self.path, 'w') as notebook_file:
            notebook_file.write(first_line)
            for note in self.notes:
                notebook_file.write(note)

    def add(self, *args):
        note = '- ' + ' '.join(args) + '\n'
        self.notes.append(note)
        print(f'Note added to @{self.name}: {note}', end='')
        self.save()

    def view_notes(self, number=None):
        if number is None or number.isdigit():
            if number is None:
                number = len(self.notes)
            elif number.isdigit():
                if int(number) < len(self.notes):
                    number = int(number)
                else:
                    number = len(self.notes)
            notes = [f'[{count+1}] ' + note for count, note in enumerate(self.notes)]
            n = len(notes)-number
            print(f'{self.name} notes:')
            for note in notes[n:]:
                print(note, end='')
        else:
            print("TypeError: Argument for 'ls' or 'ls @<notebook>' must be an integer.")

    def delete_notes_range(self, start, end):
        if start.isdigit() and end.isdigit():
            start = int(start)-1
            end = int(end)-1
            if end < len(self.notes) and start >=0:
                print(f'Delete from {self.name}:')
                for i in range(start, end+1):
                    print(f'[{i+1}] - {self.notes[i][2:-1]}')
                delete_prompt = input('Confirm: y/n? ')
                if delete_prompt in ('y', 'yes', 'Y'):
                    del self.notes[start:end+1]
                    print(f'Notes deleted from {self.name}!')
                    self.save()
            else:
                print('ValueError: Note numbers out of range.')
        else:
            print("TypeError: arguments for 'remove range' must be integers.")

    def delete_notes(self, *args):
        only_digits = all([True if arg.isdigit() else False for arg in args])
        if only_digits:
            note_indices = [int(index)-1 for index in args]
            if max(note_indices) < len(self.notes):
                print(f'Delete from {self.name}:')
                for note_index in note_indices:
                    print(f'[{note_index+1}] - {self.notes[note_index][2:-1]}')
                delete_prompt = input('Confirm: y/n? ')
                if delete_prompt in ('y', 'yes', 'Y'):
                    notes_indices_sorted = sorted(list(note_indices), reverse=True)
                    for i in notes_indices_sorted:
                        del self.notes[i]
                    print(f'Note(s) deleted from {self.name}!')
                    self.save()
            else:
                print('ValueError: Note number note in range.')
        else:
            print('TypeError: Note numbers must be integers.')

def main():
    notebooks = NotebookCollection()
    miniparser.add_command('add', notebooks.add_cmd, nargs=-1, help='add note or add notebook')
    miniparser.add_command('ls', notebooks.ls_cmd, nargs=2, help='list/view notes')
    miniparser.add_command('ls @', notebooks.list_notebooks, nargs=1, help='list notebooks')
    miniparser.add_command('rm', notebooks.delete_notes_or_notebook_cmd, nargs=-1, help='delete notes or notebook')
    miniparser.add_command('rm range', notebooks.delete_notes_range_cmd, nargs=3, help='delete range of notes')
    miniparser.add_command('set active', notebooks.set_active_notebook, nargs=1, help='set active notebook')
    miniparser.add_command('get active', notebooks.get_active_notebook, nargs=0, help='print active notebook')
    miniparser.add_command('get notebooks path', notebooks.get_custom_notebooks_path, nargs=0, help='get notebooks directory path')
    miniparser.add_command('set notebooks path', notebooks.set_custom_notebooks_path, nargs=1, help='set notebooks directory path')
    miniparser.parser()

if __name__ == "__main__":
    main()