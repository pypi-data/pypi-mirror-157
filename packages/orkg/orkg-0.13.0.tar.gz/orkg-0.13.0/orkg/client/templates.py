from orkg.utils import NamespacedClient
from orkg.out import OrkgResponse
from orkg.convert import JsonLDConverter
from typing import Dict, List, Union, Tuple, Optional
import re
from tqdm import tqdm
import json
import types
import keyword
import datetime
from random import randint

NATIVE_TYPES = ['Number', 'String', 'Boolean', 'Integer', 'Date']

LOADING_MSG = ["Reticulating splines...", "Generating witty dialog...", "Swapping time and space...", "Spinning violently around the y-axis...", "Tokenizing real life...", "Bending the spoon...", "Filtering morale...", "Don't think of purple hippos...", "We need a new fuse...", "Have a good day.", "Upgrading Windows, your PC will restart several times. Sit back and relax.", "640K ought to be enough for anybody", "The architects are still drafting", "The bits are breeding", "We're building the buildings as fast as we can", "Would you prefer chicken, steak, or tofu?", "(Pay no attention to the man behind the curtain)", "...and enjoy the elevator music...", "Please wait while the little elves draw your map", "Don't worry - a few bits tried to escape, but we caught them", "Would you like fries with that?", "Checking the gravitational constant in your locale...", "Go ahead -- hold your breath!", "...at least you're not on hold...", "Hum something loud while others stare", "You're not in Kansas any more", "The server is powered by a lemon and two electrodes.", "Please wait while a larger software vendor in Seattle takes over the world", "We're testing your patience", "As if you had any other choice", "Follow the white rabbit", "Why don't you order a sandwich?", "While the satellite moves into position", "keep calm and npm install", "The bits are flowing slowly today", "Dig on the 'X' for buried treasure... ARRR!", "It's still faster than you could draw it", "The last time I tried this the monkey didn't survive. Let's hope it works better this time.", "I should have had a V8 this morning.", "My other loading screen is much faster.", "Testing on Timmy... We're going to need another Timmy.", "Reconfoobling energymotron...", "(Insert quarter)", "Are we there yet?", "Have you lost weight?", "Just count to 10", "Why so serious?", "It's not you. It's me.", "Counting backwards from Infinity", "Don't panic...", "Embiggening Prototypes", "Do not run! We are your friends!", "Do you come here often?", "Warning: Don't set yourself on fire.", "We're making you a cookie.", "Creating time-loop inversion field", "Spinning the wheel of fortune...", "Loading the enchanted bunny...", "Computing chance of success", "I'm sorry Dave, I can't do that.", "Looking for exact change", "All your web browser are belong to us", "All I really need is a kilobit.", "I feel like im supposed to be loading something. . .", "What do you call 8 Hobbits? A Hobbyte.", "Should have used a compiled language...", "Is this Windows?", "Adjusting flux capacitor...", "Please wait until the sloth starts moving.", "Don't break your screen yet!", "I swear it's almost done.", "Let's take a mindfulness minute...", "Unicorns are at the end of this road, I promise.", "Listening for the sound of one hand clapping...", "Keeping all the 1's and removing all the 0's...", "Putting the icing on the cake. The cake is not a lie...", "Cleaning off the cobwebs...", "Making sure all the i's have dots...", "We need more dilithium crystals", "Where did all the internets go", "Connecting Neurotoxin Storage Tank...", "Granting wishes...", "Time flies when you’re having fun.", "Get some coffee and come back in ten minutes..", "Spinning the hamster…", "99 bottles of beer on the wall..", "Stay awhile and listen..", "Be careful not to step in the git-gui", "You edhall not pass! yet..", "Load it and they will come", "Convincing AI not to turn evil..", "There is no spoon. Because we are not done loading it", "Your left thumb points to the right and your right thumb points to the left.", "How did you get here?", "Wait, do you smell something burning?", "Computing the secret to life, the universe, and everything.", "When nothing is going right, go left!!...", "I love my job only when I'm on vacation...", "i'm not lazy, I'm just relaxed!!", "Never steal. The government hates competition....", "Why are they called apartments if they are all stuck together?", "Life is Short – Talk Fast!!!!", "Optimism – is a lack of information.....", "Save water and shower together", "Whenever I find the key to success, someone changes the lock.", "Sometimes I think war is God’s way of teaching us geography.", "I’ve got problem for your solution…..", "Where there’s a will, there’s a relative.", "Adults are just kids with money.", "I think I am, therefore, I am. I think.", "You don’t pay taxes—they take taxes.",  "I am free of all prejudices. I hate everyone equally.", "git happens", "May the forks be with you", "A commit a day keeps the mobs away", "This is not a joke, it's a commit.", "Constructing additional pylons...", "Roping some seaturtles...", "Locating Jebediah Kerman...", "We are not liable for any broken screens as a result of waiting.", "Hello IT, have you tried turning it off and on again?", "If you type Google into Google you can break the internet", "Well, this is embarrassing.", "What is the airspeed velocity of an unladen swallow?", "Hello, IT... Have you tried forcing an unexpected reboot?", "They just toss us away like yesterday's jam.", "They're fairly regular, the beatings, yes. I'd say we're on a bi-weekly beating.", "The Elders of the Internet would never stand for it.", "Space is invisible mind dust, and stars are but wishes.", "Didn't know paint dried so quickly.", "Everything sounds the same", "I'm going to walk the dog", "I didn't choose the engineering life. The engineering life chose me.", "Dividing by zero...", "Spawn more Overlord!", "If I’m not back in five minutes, just wait longer.", "Some days, you just can’t get rid of a bug!", "We’re going to need a bigger boat.", "Chuck Norris never git push. The repo pulls before.", "Web developers do it with <style>", "I need to git pull --my-life-together", "Java developers never RIP. They just get Garbage Collected.", "Cracking military-grade encryption...", "Simulating traveling salesman...", "Proving P=NP...", "Entangling superstrings...", "Twiddling thumbs...", "Searching for plot device...", "Trying to sort in O(n)...", "Laughing at your pictures-i mean, loading...", "Sending data to NS-i mean, our servers.", "Looking for sense of humour, please hold on.", "Please wait while the intern refills his coffee.", "A different error message? Finally, some progress!", "Hold on while we wrap up our git together...sorry", "Please hold on as we reheat our coffee", "Kindly hold on as we convert this bug to a feature...", "Kindly hold on as our intern quits vim...", "Winter is coming...", "Installing dependencies", "Switching to the latest JS framework...", "Distracted by cat gifs", "Finding someone to hold my beer", "BRB, working on my side project", "@todo Insert witty loading message", "Let's hope it's worth the wait", "Aw, snap! Not..", "Ordering 1s and 0s...", "Updating dependencies...", "Whatever you do, don't look behind you...", "Please wait... Consulting the manual...", "It is dark. You're likely to be eaten by a grue.", "Loading funny message...", "It's 10:00pm. Do you know where your children are?", "Waiting Daenerys say all her titles...", "Feel free to spin in your chair", "What the what?", "format C: ...", "Forget you saw that password I just typed into the IM ...", "What's under there?", "Your computer has a virus, its name is Windows!", "Go ahead, hold your breath and do an ironman plank till loading complete", "Bored of slow loading spinner, buy more RAM!", "Help, I'm trapped in a loader!", "What is the difference btwn a hippo and a zippo? One is really heavy, the other is a little lighter", "Please wait, while we purge the Decepticons for you. Yes, You can thanks us later!", "Chuck Norris once urinated in a semi truck's gas tank as a joke....that truck is now known as Optimus Prime.", "Chuck Norris doesn’t wear a watch. HE decides what time it is.", "Mining some bitcoins...", "Downloading more RAM..", "Updating to Windows Vista...", "Deleting System32 folder", "Hiding all ;'s in your code", "Alt-F4 speeds things up.", "Initializing the initializer...", "When was the last time you dusted around here?", "Optimizing the optimizer...", "Last call for the data bus! All aboard!", "Running swag sticker detection...", "Never let a computer know you're in a hurry.", "A computer will do what you tell it to do, but that may be much different from what you had in mind.", "Some things man was never meant to know. For everything else, there's Google.", "Unix is user-friendly. It's just very selective about who its friends are.", "Shovelling coal into the server", "Pushing pixels...", "How about this weather, eh?", "Building a wall...", "Everything in this universe is either a potato or not a potato", "The severity of your issue is always lower than you expected.", "Updating Updater...", "Downloading Downloader...", "Debugging Debugger...", "Reading Terms and Conditions for you.", "Digested cookies being baked again.", "Live long and prosper.", "There is no cow level, but there's a goat one!", "Running with scissors...", "Definitely not a virus...", "You may call me Steve.", "You seem like a nice person...", "Coffee at my place, tommorow at 10A.M. - don't be late!", "Work, work...", "Patience! This is difficult, you know...", "Discovering new ways of making you wait...", "Your time is very important to us. Please wait while we ignore you...", "Time flies like an arrow; fruit flies like a banana", "Two men walked into a bar; the third ducked...", "Sooooo... Have you seen my vacation photos yet?", "Sorry we are busy catching em' all, we're done soon", "TODO: Insert elevator music", "Still faster than Windows update", "Composer hack: Waiting for reqs to be fetched is less frustrating if you add -vvv to your command.", "Please wait while the minions do their work", "Grabbing extra minions", "Doing the heavy lifting", "We're working very Hard .... Really", "Waking up the minions", "You are number 2843684714 in the queue", "Please wait while we serve other customers...", "Our premium plan is faster", "Feeding unicorns..."]


def pre_process_string(string: str) -> str:
    lower_string = string.lower().replace(' ', '_')
    res = re.sub(r'\W+', '', lower_string)
    return res


def check_against_keywords(string: str) -> str:
    """
    Checks a string against python keywords.
    If a keyword is found, it is postfixed with a '_template'.
    """
    if string in keyword.kwlist:
        return string + '_template'
    return string


def clean_up_dict(dictionary: dict) -> dict:
    """
    replaces the key 'name' with 'label' inside the 'resource' object.
    then strips the root key 'resource' and returns the inner dictionary.
    """
    dictionary = dictionary['resource']
    dictionary['label'] = dictionary['name']
    del dictionary['name']
    return dictionary


def remove_empty_values(dictionary: dict):
    if 'values' not in dictionary['resource']:
        return
    for _, value in dictionary['resource']['values'].items():
        for v in value:
            if not bool(v):
                value.remove(v)


def map_type_to_pythonic_type(value_type: str) -> str:
    if value_type == 'Number':
        return 'Union[int, float, complex]'
    elif value_type == 'Boolean':
        return 'bool'
    elif value_type == 'Integer':
        return 'int'
    elif value_type == 'Date':
        return 'datetime.date'
    else:
        return 'str'


class ObjectStatement(object):
    # Optionals
    label: Optional[str]
    classes: Optional[List[str]]
    text: Optional[str]
    datatype: Optional[str]
    values: Optional[List]
    name: Optional[str]
    # Must have
    predicate_id: str
    template_id: str

    def __init__(self, predicate_id: str, template_id: str):
        self.predicate_id = predicate_id
        self.template_id = template_id
        self.label = None
        self.classes = None
        self.text = None
        self.datatype = None
        self.values = None
        self.name = None

    @staticmethod
    def create_main(name: str, classes: List[str] = None) -> 'ObjectStatement':
        statement = ObjectStatement('', '')
        statement.set_main_statement(name, classes)
        return statement

    @property
    def is_main_statement(self) -> bool:
        return self.name is not None

    def set_main_statement(self, name: str, classes: List[str] = None):
        self.name = name
        self.classes = classes

    def set_literal(self, text: str, datatype: Optional[str] = None):
        self.text = text
        self.datatype = datatype

    def set_nested_statement(self, statement: 'ObjectStatement'):
        self.set_resource(statement.label, statement.classes)
        for value in statement.values:
            self.add_value(value)

    def set_resource(self, label: str, classes: List[str] = None):
        self.label = label
        self.classes = classes

    def add_value(self, value: 'ObjectStatement'):
        if self.values is None:
            self.values = []
        self.values.append(value)

    def values_to_statements(self) -> str:
        if self.values is None:
            return '{}'
        return '{' + ', '.join([f'"{v.predicate_id}": [{{{v.to_statement()}}}]' for v in self.values]) + '}'

    def to_statement(self) -> str:
        statement = ""
        if self.text is not None:
            statement += f'"text": {self.text}'
            if self.datatype is not None:
                statement += f', "datatype": "{self.datatype}"'
        elif self.label is not None:
            statement += f'"label": {self.label}'
            if self.classes is not None:
                statement += f', "classes": {self.classes}'
            if self.values is not None:
                statement += f', "values": {self.values_to_statements()} '
        return statement

    def serialize(self) -> str:
        if self.is_main_statement:
            return f'{{ "resource": {{ "name": "{self.name}", "classes": {self.classes}, "values": {self.values_to_statements()} }} }}'
        else:
            return f'"{self.predicate_id}": [{{{self.to_statement()}}}]'


class TemplateInstance(object):
    """
    A class that takes a dictionary in the constructor
    With methods to serialize the dictionary to a file, pretty print it, and send it to the KG.
    """
    def __init__(self, template_dict, orkg_client) -> None:
        self.template_dict = template_dict
        self.client = orkg_client
        self.preprocess_dict()

    def preprocess_dict(self):
        if isinstance(self.template_dict, str):
            self.template_dict = self.template_dict.strip("'<>() ").replace('\'', '\"')
            self.template_dict = json.loads(self.template_dict)

    def serialize_to_file(self, file_path: str, as_jsonld: bool = False) -> None:
        """
        Serializes the template to a file.
        :param as_jsonld: whether to serialize the data as JSON-LD
        :param file_path: the file path to save the template to
        """
        with open(file_path, 'w') as f:
            if as_jsonld:
                json.dump(JsonLDConverter().convert_2_jsonld(self.template_dict), f, indent=4)
            else:
                json.dump(self.template_dict, f, indent=4)

    def pretty_print(self, as_jsonld: bool = False) -> None:
        """
        Pretty prints the template to the console.
        :param as_jsonld: whether to print the data as JSON-LD
        """
        if as_jsonld:
            print(json.dumps(JsonLDConverter().convert_2_jsonld(self.template_dict), indent=4))
        else:
            print(json.dumps(self.template_dict, indent=4))

    def save(self) -> OrkgResponse:
        """
        Saves the template to the server.
        :return: The OrkgResponse from the server
        """
        return self.client.objects.add(params=self.template_dict)

    @staticmethod
    def parse_dict(dictionary: Dict, obj: ObjectStatement) -> None:
        if 'resource' in dictionary:
            # This is a complete resource and not a nested one
            dictionary = dictionary['resource']
            obj.set_resource(dictionary['name'], dictionary['classes'])
            if 'values' in dictionary:
                dictionary = dictionary['values']
        for key, values in dictionary.items():
            for value in values:
                sub_obj = ObjectStatement(key, obj.template_id)
                obj.add_value(sub_obj)
                if 'text' in value:
                    datatype = value.get('datatype', None)
                    sub_obj.set_literal(f"\"{value['text']}\"", datatype)
                elif 'label' in value:
                    classes = value.get('classes', None)
                    sub_obj.set_resource(f"\"{value['label']}\"", classes)
                    if 'values' in value:
                        TemplateInstance.parse_dict(value['values'], sub_obj)


class TemplateComponent:
    predicate_id: str
    predicate_label: str
    value_class_id: Optional[str]
    value_class_label: Optional[str]
    is_of_custom_type: bool
    min_cardinality: Optional[int]
    max_cardinality: Optional[int]
    is_nested_template: bool
    nested_template_target: Optional[str]

    # private properties
    _orkg_client: NamespacedClient

    def __init__(self, orkg_client, component_id: str):
        self._orkg_client = orkg_client
        component_statements = orkg_client.statements.get_by_subject(subject_id=component_id).content
        # Set predicate info
        predicate = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentProperty', component_statements)
        )[0]['object']
        self.predicate_id = predicate['id']
        self.predicate_label = predicate['label']
        # Set class value, id, and label
        value_class = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentValue', component_statements)
        )
        if len(value_class) == 0:
            self.value_class_id = 'String'
            self.value_class_label = 'Text'
            self.is_of_custom_type = False
        else:
            value_class = value_class[0]['object']
            self.value_class_id = value_class['id']
            self.value_class_label = value_class['label']
            self.is_of_custom_type = True if self.value_class_id not in NATIVE_TYPES else False
        # Set cardinality of the property
        max_cardinality = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentOccurrenceMax', component_statements)
        )
        self.max_cardinality = None if len(max_cardinality) == 0 else max_cardinality[0]['object']['label']
        mix_cardinality = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateComponentOccurrenceMin', component_statements)
        )
        self.mix_cardinality = None if len(mix_cardinality) == 0 else mix_cardinality[0]['object']['label']
        # Set if the component is nested template
        if not self.is_of_custom_type:
            self.is_nested_template = False
        else:
            template_classes = orkg_client.statements.get_by_object_and_predicate(object_id=self.value_class_id,
                                                                                  predicate_id='TemplateOfClass').content
            if len(template_classes) == 0:
                self.is_nested_template = False
            else:
                self.is_nested_template = True
                self.nested_template_target = template_classes[0]['subject']['id']

    def get_clean_name(self) -> str:
        return pre_process_string(check_against_keywords(self.predicate_label))

    def get_return_type(self) -> str:
        if self.is_nested_template:
            return 'TemplateInstance'
        return map_type_to_pythonic_type(self.value_class_id)

    def get_property_as_function_parameter(self) -> str:
        clean_label = self.get_clean_name()
        return_type = self.get_return_type()
        return f'{clean_label}: {return_type}'

    def get_param_documentation(self) -> str:
        if self.is_nested_template:
            target_template = Template.find_or_create_template(self._orkg_client, self.nested_template_target)
            return f':param {self.get_clean_name()}: a nested template, use orkg.templates.{target_template.get_template_name_as_function_name()}'
        else:
            # component is not nested template, return normal documentation
            return f':param {self.get_clean_name()}: a parameter of type {self.value_class_label}'

    def create_object_statement(self) -> ObjectStatement:
        to_str = self.get_return_type() == 'datetime.date'
        value = self.get_clean_name()
        statement = ObjectStatement(self.predicate_id, "UNKNOWN")  # FIXME: template_id is unknown in this scope
        if not self.is_nested_template:
            if self.is_of_custom_type:
                statement.set_resource(
                    label=f'str({value})' if to_str else value,
                    classes=[self.value_class_id]
                )
            else:
                statement.set_literal(
                    text=f'str({value})' if to_str else value,
                    datatype=None  # FIXME: datatype is not set for literals
                )
        return statement

    def __str__(self):
        return f'{"N" if self.is_nested_template else ""}Property(id="{self.predicate_id}", label="{self.predicate_label}", class="{self.value_class_id}", cardinality=({self.min_cardinality}, {self.max_cardinality}))'


class Template(object):
    # Static variable to keep track of all templates
    templates: Dict = {}

    # Instance variables
    template_class: str
    is_formatted: bool
    template_id: str
    template_name: str
    components: List[TemplateComponent]

    def __init__(self, orkg_client, template_id: str):
        # Fetch template statements
        self.components = []
        template_statements = orkg_client.statements.get_by_subject(subject_id=template_id).content
        # Iterate over template statements and create template components
        components = filter(lambda x: x['predicate']['id'] == 'TemplateComponent', template_statements)
        for component in components:
            self.components.append(TemplateComponent(orkg_client, component['object']['id']))
        # Set template class
        self.template_class = list(
            filter(lambda x: x['predicate']['id'] == 'TemplateOfClass', template_statements)
        )[0]['object']['id']
        # Set template info
        self.template_id = template_id
        self.template_name = orkg_client.resources.by_id(id=template_id).content['label']
        self.is_formatted = len(
            list(filter(lambda x: x['predicate']['id'] == 'TemplateLabelFormat', template_statements))
        ) > 0
        # Register template to the global templates dict
        Template.templates[template_id] = self

    @staticmethod
    def find_or_create_template(orkg_client, template_id: str) -> 'Template':
        """
        Check if template is in registry, if yes return it.
        Otherwise, instantiate a new template.
        """
        if template_id in Template.templates:
            return Template.templates[template_id]
        else:
            return Template(orkg_client, template_id)

    def get_params_as_function_params(self) -> Tuple[str, str]:
        """
        Returns a tuple of the function parameters for the template.
        The first element is the function parameters as a string,
        the second element is the function docstring as a string.
        """
        params = ', '.join([c.get_property_as_function_parameter() for c in self.components])
        if not self.is_formatted:
            params = f'label: str, {params}'
            if params.strip()[-1] == ',':
                params = params.strip()[:-1]
        params_docstring = '\n\t'.join(
            [
                comp.get_param_documentation()
                for comp in self.components
            ]
        )
        if not self.is_formatted:
            params_docstring = f':param label: the label of the resource of type string\n\t{params_docstring}'
        return params, params_docstring

    def get_template_name_as_function_name(self) -> str:
        return check_against_keywords(pre_process_string(self.template_name))

    def create_api_object_values_and_classes(self) -> Tuple[str, str]:
        """
        Returns the API object values for the template.
        """
        properties = [c.create_object_statement() for c in self.components]
        #  return f""""values": {{{','.join(properties)}}}""", f'"classes": ["{self.template_class}"]'
        return f""""values": {{{','.join([p.serialize() for p in properties])}}}""", f'"classes": ["{self.template_class}"]'

    def create_api_object(self):
        """
        Returns the complete ORKG API object for the template as string.
        """
        values, classes = self.create_api_object_values_and_classes()
        object_json = f"""{{
                "resource": {{
                    "name": {'""' if self.is_formatted else 'label'},
                    {classes},
                    {values}
                }}
            }}"""
        return object_json

    def __str__(self):
        return f'Template(id="{self.template_id}", class="{self.template_class}", components= "{len(self.components)} comps."))'


class OTFFunctionWriter(object):

    @staticmethod
    def implement_function(
            orkg_context: NamespacedClient,
            template_id: str,
            print_function: bool = False
    ):
        template = Template.find_or_create_template(orkg_context.client, template_id)
        params, params_docstring = template.get_params_as_function_params()
        object_json = template.create_api_object()
        lookup_map = {component.get_clean_name(): component.predicate_id for component in template.components}
        function_name = check_against_keywords(pre_process_string(template.template_name))
        new_method = f'''
def {function_name}(self, {params}) -> TemplateInstance:
    """ Creates a template of type {template_id} ({template.template_name})

    {params_docstring}
    :return: a string representing the resource ID of the newly created resource
    """
    lookup_map = {lookup_map}
    obj = ObjectStatement.create_main({'""' if template.is_formatted else 'label'}, ['{template.template_class}'])
    TemplateInstance.parse_dict({object_json},obj)
    obj = TemplateInstance(obj.serialize(), self.client).template_dict
    for param_name, nested_template in {{k: v for k, v in locals().items() if isinstance(v, TemplateInstance)}}.items():
        predicate_id = lookup_map[param_name]
        if 'values' not in obj['resource']:
            obj['resource']['values'] = {{}}
        if not predicate_id in obj['resource']['values']:
            obj['resource']['values'][predicate_id] = []
        obj['resource']['values'][predicate_id].append(clean_up_dict(nested_template.template_dict))
    remove_empty_values(obj)
    return TemplateInstance(obj, self.client)

orkg_context.client.templates.{function_name} = types.MethodType( {function_name}, orkg_context )
                    '''
        if print_function:
            print(new_method)
        exec(new_method)


class TemplatesClient(NamespacedClient):
    templates: Dict = {}

    def materialize_template(self, template_id: str):
        return self.fetch_and_build_template_function(template_id)

    def materialize_templates(self, templates: Optional[List[str]] = None):
        if templates is None:
            templates = [template['id'] for template in
                         self.client.classes.get_resource_by_class(class_id='ContributionTemplate', size=1000).content]
        exclude = ['R12000', 'R38504', 'R108555', 'R111221', 'R111231', 'R70785', 'R48000', 'R111155']  # RF, RP, Comp last 3
        count = 0
        with tqdm(templates, desc='Materializing templates') as pbar:
            for template_id in pbar:
                if template_id not in exclude:
                    self.materialize_template(template_id)
                if not count % 10:
                    pbar.set_description(LOADING_MSG[randint(0, len(LOADING_MSG)-1)], refresh=True)
                count += 1

    def fetch_and_build_template_function(self, template_id: str):
        OTFFunctionWriter.implement_function(self, template_id, False)
        return True

    def lookup_template(self, template_id: str):
        if template_id in self.templates:
            return self.templates[template_id]
        else:
            return None

    def register_template(self, template_id: str, template_class):
        self.templates[template_id] = template_class

    def get_template_specifications(self, template_id: str) -> str:
        template = Template(self.client, template_id)
        result = {comp.get_clean_name(): f'A value of type ({comp.value_class_label})' for comp in template.components}
        return json.dumps(result, indent=4, sort_keys=True, default=str)

    def create_template_instance(self, template_id: str, instance: Dict) -> str:
        """
        Creates an instance of a given template by filling in
        the specifications of the template with the provided values

        :param template_id: the string representing the template ID
        :param instance: the json object that contains the components of the template instance
        """
        template = Template(self.client, template_id)
        obj = template.create_api_object()
        for key, value in instance.items():
            obj = obj.replace(key, f'"{value}"')
        json_object = json.loads(obj)
        return self.client.objects.add(params=json_object).content['id']
