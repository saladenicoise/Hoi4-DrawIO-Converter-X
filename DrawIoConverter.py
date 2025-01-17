# by Flaxbeard fixed by nika and Ysiki
# Updated by Salad#0101 for use with Avalanche v1.12
# version 0.3.0, 2023-05-03

import re
import os
from html import unescape
import tkinter as tk
from math import inf as INF
from tkinter.scrolledtext import ScrolledText

# Base structure of a focus
BASE_FOCUS = '''
    focus = {
	    id = <tag>
	    icon = GFX_generic_suspend_constitution
	    cost = 5
	    x = <x>
	    y = <y>
	    ai_will_do = {
		    factor = 1
	    }
	    completion_reward = {
		    log = "[GetDateText]: [Root.GetName]: Focus <tag>"
	    }
        <prereqs><exclusives>
    }
'''

# Regex to find focuses in the draw.io file (boxes), these have a stroke
BOX_REGEX = re.compile(
    r'(<mxCell.*value((?!strokeColor=none).)*?>[\s\S]*?</mxCell>)', re.MULTILINE)

# Regex to find arrows (have a source and target set to boxes)
ARROW_REGEX = re.compile(r'(<mxCell.*source.*target.*>)')

# Regex to extract various properties of arrows
SOURCE_REGEX = re.compile(r'source="([^"]*)"')
TARGET_REGEX = re.compile(r'target="([^"]*)"')

# Regex to extract various properties of focus boxes
VALUE_REGEX = re.compile(r'value="([^"]*)"')
ID_REGEX = re.compile(r'id="([^"]*)"')
X_REGEX = re.compile(r' x="([^"]*)"')
Y_REGEX = re.compile(r' y="([^"]*)"')

# Regex to find and remove HTML tags or excess spaces
TAG_REGEX = re.compile(r'<.*?>')
SPACE_REGEX = re.compile(r'\s+')

# Regex to filter characters that can't be used in a focus ID
NON_ALPHANUMERIC_REGEX = re.compile(r'[^a-zA-Z0-9_]+')


class Focus:
    """Represents a single focus"""

    def __init__(self, focus_id, focus_tag, focus_name=None):
        self.id = focus_id
        self.tag = focus_tag
        self.name = focus_name
        self.prerequisites = []
        self.dashed_prerequisites = []
        self.exclusives = []
        self.relative = None
        self.raw_x = 0
        self.raw_y = 0
        self.x = 0
        self.y = 0
        self.rel_x = 0
        self.rel_y = 0


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.select_image_file = ''
        self.select_music_file = ''
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        """Set up GUI"""
        self.run_script = tk.Button(self)
        self.run_script['text'] = 'Run Program'
        self.run_script['command'] = self.run_app
        self.run_script.pack(side='top', pady=5)

        self.output_text = tk.StringVar(value='Ready for running')
        self.output_label = tk.Label(self, textvariable=self.output_text)
        self.output_label['wraplength'] = 480
        self.output_label.pack(side='top', pady=5)

        self.country_tag_label = tk.Label(self)
        self.country_tag_label['text'] = 'Country Tag\n(USA, MEX, BRA)'
        self.country_tag_label['wraplength'] = 170
        self.country_tag_label.pack(side='top', pady=5)
        self.country_tag = tk.Entry(self)
        self.country_tag.pack(side='top', pady=5)

        self.horiz_spacing_label = tk.Label(self)
        self.horiz_spacing_label['text'] = 'Horizontal Spacing (Higher is Tighter):'
        self.horiz_spacing_label.pack(side='top', pady=5)
        self.horiz_spacing = tk.Scale(self, from_=25, to=300, orient=tk.HORIZONTAL,
                                      resolution=1,  command=self.update_positions, length=400)
        self.horiz_spacing.set(70)
        self.horiz_spacing.pack(side='top', pady=5)

        self.vert_spacing_label = tk.Label(self)
        self.vert_spacing_label['text'] = 'Vertical Spacing (Higher is Tighter):'
        self.vert_spacing_label.pack(side='top', pady=5)
        self.vert_spacing = tk.Scale(self, from_=25, to=300, orient=tk.HORIZONTAL,
                                     resolution=1,  command=self.update_positions, length=400)
        self.vert_spacing.set(80)
        self.vert_spacing.pack(side='top', pady=5)

        self.drawio_data_label = tk.Label(self)
        self.drawio_data_label['text'] = 'Draw.io Data\n(Copied from Extras -> Edit Diagram)'
        self.drawio_data_label.pack(side='top', pady=5)

        self.drawio_data = ScrolledText(self, width=50, height=15, wrap="word")
        self.drawio_data.pack(side='top', pady=5)

    def update_positions(self, _=0):
        self.horiz_spacing_amnt = self.horiz_spacing.get()
        self.vert_spacing_amnt = self.vert_spacing.get()

    def run_app(self):
        country_tag = self.country_tag.get()
        if country_tag is None or country_tag == "":
            country_tag = "DEF"

        foci = {}
        i_contents = self.drawio_data.get(1.0, tk.END).strip()

        # Process all focus boxes
        for e in BOX_REGEX.findall(i_contents):
            focus_id = ID_REGEX.findall(e[0])[0]

            #
            text = VALUE_REGEX.findall(e[0])[0]
            text = unescape(text).replace('&nbsp;', ' ')
            text = re.sub(TAG_REGEX, ' ', text)
            text = re.sub(SPACE_REGEX, '_', text)
            text = text.strip()
            

            # Break if no name (false positive)
            if not text:
                continue

            focus_x = X_REGEX.findall(e[0])[0]
            focus_y = Y_REGEX.findall(e[0])[0]

            focus_name = text

            focus_tag = re.sub(NON_ALPHANUMERIC_REGEX, '',
                               text)
            focus_tag = f'{country_tag}_{focus_tag}'

            focus = Focus(focus_id, focus_tag, focus_name)

            focus.raw_x = float(focus_x)
            focus.raw_y = float(focus_y)

            foci[focus_id] = focus

        # Process all arrows
        for e in ARROW_REGEX.findall(i_contents):
            source = SOURCE_REGEX.findall(e)[0]
            target = TARGET_REGEX.findall(e)[0]

            s_focus = foci[source]
            t_focus = foci[target]

            # Arrows between objects on the same y-level indicate mutually exclusive
            if abs(s_focus.raw_y - t_focus.raw_y) < 10:
                if target not in s_focus.exclusives:
                    s_focus.exclusives.append(target)
                    t_focus.exclusives.append(source)
            else:
                # Dashed arrows indicate that either focus can be a prereq, otherwise normal prereq
                if 'dash' in e:
                    t_focus.dashed_prerequisites.append(source)
                else:
                    t_focus.prerequisites.append(source)

        # Find the uppermost and leftmost focus, to set the origin point
        base_x = INF
        base_y = INF
        for focus_id in foci:
            focus = foci[focus_id]
            if focus.raw_x < base_x:
                base_x = focus.raw_x
            if focus.raw_y < base_y:
                base_y = focus.raw_y

        # Set the x and y position in terms of focus tree positioning based on the diagram position
        for focus_id in foci:
            foci[focus_id].x = round(
                (foci[focus_id].raw_x - base_x) / self.horiz_spacing_amnt)
            foci[focus_id].y = round(
                (foci[focus_id].raw_y - base_y) / self.vert_spacing_amnt)

        # Use relative positioning where possible
        for focus_id in foci:
            focus = foci[focus_id]

            all_prereqs = focus.prerequisites + focus.dashed_prerequisites
            if len(all_prereqs) > 0:
                focus.relative = all_prereqs[0]
                focus.rel_x = round(
                    (focus.raw_x - foci[focus.relative].raw_x) / self.horiz_spacing_amnt)
                focus.rel_y = round(
                    (focus.raw_y - foci[focus.relative].raw_y) / self.vert_spacing_amnt)

        # Output the foci
        out = '''
focus_tree = {
    id = ''' + country_tag.lower() + '''
            
	country = {
		factor = 0
		modifier = {
		    add = 10
			tag = ''' + country_tag + '''
		}
	}
            
	continuous_focus_position = { 
		x = 0
		y = 0
    }
'''
        for focus_id in foci:
            focus = foci[focus_id]

            # Assemble prerequisite code
            prereqs_code = ''
            for prereq in focus.prerequisites:
                prereqs_code += f'\t\tprerequisite = {{ focus = {foci[prereq].tag} }}\n'
            if len(focus.dashed_prerequisites) > 0:
                prereqs_code += '\t\tprerequisite = {\n'
                for prereq in focus.dashed_prerequisites:
                    prereqs_code += f'\t\tfocus = {foci[prereq].tag}\n'
                prereqs_code += '\t}\n'

            # Assemble mutually exclusive code
            exclusives_code = ''
            for exclusive in focus.exclusives:
                exclusives_code += f'\t\tmutually_exclusive = {{ focus = {foci[exclusive].tag} }}\n'
            focus_code = BASE_FOCUS.replace('<tag>', focus.tag)

            # Assemble positioning code
            if focus.relative:
                prereqs_code = f'relative_position_id = {foci[focus.relative].tag}\n' + prereqs_code
                focus_code = focus_code.replace('<x>', str(
                    focus.rel_x)).replace('<y>', str(focus.rel_y))
            else:
                focus_code = focus_code.replace(
                    '<x>', str(focus.x)).replace('<y>', str(focus.y))

            # Output focus code
            focus_code = focus_code.replace('<prereqs>', prereqs_code).replace(
                '<exclusives>', exclusives_code)
            out += focus_code

        # Output focus loc
        out_loc = 'l_english:\n'
        for focus_id in foci:
            focus = foci[focus_id]
            out_loc += f' {focus.tag}:0 "{focus.name}"\n'
            out_loc += f' {focus.tag}_desc:0 "{focus.name}_desc"\n'

        os.makedirs("output", exist_ok=True)
        with open(f'output/{country_tag}.txt', 'w') as o_file:
            o_file.write(out)
            o_file.write("}")

        with open(f'output/mod{country_tag}_l_english.yml', 'w', encoding='utf-8-sig') as o_file:
            o_file.write(out_loc)

        self.output_text.set(
            f"Country {country_tag} processing was succeed! check output folder.")


root = tk.Tk()
root.geometry('500x510')
root.title('Draw.io Converter')
app = App(master=root)
app.mainloop()
