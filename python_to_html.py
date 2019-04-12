"""
A utility for extracting documentation from ptyhon files
as html websites.
"""
import os, time, shutil, inspect

__version__ = "0.x"
__repo__ = "https://github.com/TG-Techie/tg_docs_utilities"

#order style, function, class, class_function, highlight, file_start, file_end
default_template = [
#style part of string
'''
body{background-color: white;}
''',
#wrapper for a function
'''<hr><div>
    {{tag}}
    <h3>{{name}}</h3>
    <p>{{contents}}</p>
</div>
''',
#wrapper for a class
'''
<hr><div>
    {{tag}}
    <h3>{{name}}</h3>
    <p>{{contents}}</p>
</div>
''',
#wrapper for a method of a class
'''
<hr><div>
    {{tag}}
    <h3>{{name}}</h3>
    <p>{{contents}}</p>
</div>
''',
#highlight
'''<span style="background-color:#bbb;"">{{contents}}</span>''',
#start of the file
'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Docs.{{title}}</title>
    <style>{{style}}</style>
</head>
<body><!--ul--><!--start in-module objects-->
''',
#end of the file
'''<!--end in-module objects-->
<!--/ul--></body></html>''']

default_template.append(default_template[1])

current_template = default_template
def highlight_text(string):
    return current_template[4].replace('{{contents}}',string)

def parse_docstring(object, object_name, template, highlight, prefix = ''):
    """
    Parse the docs of a function, class, or method and return
    a html formatted string.
    :param object: the object to extract docs from.
    :param object_name:the desired name used in the output.
    :param template:the pre-written html to be formatted with the object specific docs.
    :param prefix: the prefix to put infron of  that name. (often 'class' or 'function')
    """
    section = template

    doc = [x.split(' ') for x in str(object.__doc__).split(':')]
    types = ['param', 'tag', 'type']

    tag=''

    num_inputs = 0
    main_desc='<i>No documentation found.</i>'
    inputs= []
    doc_out=''

    type_prefix = ''
    kwargs_hit = False
    while len(doc):
        subj = doc.pop(0)
        #print(subj[0:2])
        if subj[0] in types:
            front = subj[0]
            back = ' '.join(subj[1:])
            if front == 'tag':
                print('!tag', back, object_name)
                tag = back
            elif front == 'type':
                type_prefix = back
            elif front == 'param':
                was_highlighted = False
                formatted_input =  back.replace(' ', '&nbsp;=&nbsp;').replace("'",'"')
                if not '=' in formatted_input:
                    formatted_input = highlight_text(formatted_input)
                    was_highlighted = True
                if kwargs_hit == False and not was_highlighted:
                    #formatted_input = '<br>'+formatted_input
                    inputs.append('&nbsp;'*3+formatted_input)
                    kwargs_hit = True
                else:
                    inputs.append(formatted_input)
                num_inputs += 1

                doc_out += '\n<li>'+type_prefix+' '+ formatted_input + ':'+' '.join(doc.pop(0))+'</li>'
                type_prefix = ''
            else:
                type_prefix = ''
        else:
            main_desc = ' '.join(subj)
            if 'None'== main_desc:
                main_desc = '<i>No documentation found.</i>'

    #add the top "note"
    anchors = []
    for permu in [object_name,
                  prefix+' '+object_name,
                  tag+' '+object_name]:
        anchors.append('<a id="'+permu+'''" style='margin-top: -7.5%;
                                              padding-bottom: 7.5%;
                                              display: block;'>
                        </a>''')

    section = section.replace('{{note}}',highlight_text(tag+''.join(anchors)))

    #add in the name and prefix
    '''type func_name(in,puts,):'''
    inputstring = ''
    for inp in inputs:
        inputstring += inp +',  '
    inputstring = '('+inputstring.strip(' ').strip(',')+'):'

    name = highlight_text(prefix) # the prefix, highlighted
    name += ' '+object_name
    if not isinstance(object, property):
        name += inputstring
    else:
        name += ':'
    section = section.replace('{{name}}', name)


    #add in contents
    """
    Description
    Inputs:
    ul
        li
        li
        li
    /ul
    """
    #print(doc_out)
    #print((main_desc,subj))

    content = '<div style="margin-left:3%"><p><!--main_desc-->'+main_desc+'</p>\n<ul><!--doc_out-->'+doc_out+'</ul></div>'


    return(section.replace('{{contents}}', content))

def write_item(func, func_name, file, template, index = 1, prefix = 'function'):
    """
    From the template write the formatted docstring of the inputted function.
    :param func: the function to document
    :param func_name: the name to be used for the function.
    :param file: the file to output the documentation to.
    :param template: the list containing templates.
    """
    string = parse_docstring(func, func_name, template[index], template[4], prefix = prefix)
    #print()
    #print(func_name, '"'+string+'"')
    if len(string):
        file.write(string+'\n')

def write_class(class_obj, class_name, file, template):
    """
    From the template write the formatted docstring of the inputted class.
    :param class_obj: the class to document.
    :param class_name: the name to use when documenting, str.
    :param file: the file to write the docs into.
    :param template: the list containing templates.
    """
    attr_list = list(dir(class_obj))
    #print(class_name, attr_list)
    attr_list.sort()

    print(class_name+':')
    if '__init__' in attr_list:
        file.write(parse_docstring(eval('class_obj.__init__') ,class_name, template[2], template[4], prefix = 'class'))
    else:
        file.write(parse_docstring(class_obj, class_name, template[2], template[4], prefix = 'class'))

    #file.write('<div style="margin-left:5%">')
    #                 [[func],[property],[values?]]
    chunked_attr_list = [[], [], []]
    for attribute_name in attr_list:
        if not attribute_name.startswith('_'):
            attribute = eval('class_obj.'+attribute_name)
            if callable(attribute):
                chunked_attr_list[0].append(attribute_name)
            elif  isinstance(attribute, property):
                chunked_attr_list[1].append(attribute_name)
            else:
                chunked_attr_list[2].append(attribute_name)

    print(chunked_attr_list)
    for attribute_name in chunked_attr_list[0]:
        attribute = eval('class_obj.'+attribute_name)
        write_item(attribute, class_name+'.'+attribute.__name__, file, template, index = 3, prefix = '')

    for attribute_name in chunked_attr_list[1]:
        attribute = eval('class_obj.'+attribute_name)
        write_item(attribute, class_name+'.'+attribute_name, file, template, index = 3, prefix = '')

    for attribute_name in chunked_attr_list[2]:
        attribute = eval('class_obj.'+attribute_name)
        write_item(attribute, class_name+'.'+attribute_name, file, template, index = 3, prefix = '')
    #file.write('</div>')

def compile_page(module, output_path, template = default_template, layout = None):
    """
    Write a html document for the inputted module to the inputted location.
    :param module: the module object to document.
    :param output_path: the path in which to ouput the created html file. './' is permitted.
    :param template: a keyword input that specifies the wrapping html around documentation.
    input a list in the following order [style, function, class, class_function, file_start, file_end].
    style will be inserted into file_start in place of "{ {style}}".
    for function, class, and method  "{ {name}}" and "{ {contents}}" will be replaced with the name and content.
    file_end and file_start will take take their places respectively on each side of the file.

    """
    global current_template
    current_template = template
    print('\n', module)
    prev_path = os.path.abspath(output_path)
    file_path = os.path.abspath(output_path+'/docs/'+'/'.join(module.__name__.split('.')[0:-1]))
    module_name = module.__name__.split('.')[-1]
    file_name = module_name+'.html'
    file_title = 'Docs.'+module.__name__

    print('outputting to: "'+file_path+'/'+file_name+'"')

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    #shutil.rmtree(file_path)
    #os.makedirs(file_path)

    os.chdir(file_path)

    file = open(file_name,"w+")
    file.seek(0)

    if layout:
        file.write("""---
layout: {{layout}}
---""".replace("{{layout}}", layout))
    #print(file)

    file.write(template[len(template)-3].replace('{{style}}',template[0]).replace('{{title}}',file_title))

    #intro section
    file.write('<hr><ul>')
    file.write('<h2>'+module_name+'</h2> ')
    file.write(module.__name__)
    if hasattr(module, '__version__'):
        if module.__version__:
            file.write('<p><h3 style="display:inline;">Version:</h3> '+module.__version__+"</p>")
    if hasattr(module, '__repo__'):
        if module.__repo__:
            file.write('<p><h3 style="display:inline;">Repository:</h3> <a href="'+module.__repo__+'">'+module.__repo__+'</a></p>')
    if hasattr(module, '__doc__'):
        if module.__doc__:
            file.write('<p><h3>Description:</h3> '+module.__doc__+"</p>")



    file.write("""
    <input id="autogen_search_input">
    <style>
    a.autogen_search_anchor:active{
    background-color:darkgrey !IMPORTANT;}
    </style>
    <a
        href="#OH!NO!OurJavascriptIsNotWorkingRight"
        id="autogen_search_anchor"
        class="autogen_search_anchor"
        style="
            text-decoration: none;
            background-color:lightgrey;
            padding: .3em;
            border-radius: .3em;"
    >Search</a>
    <script>
    interval = setInterval(() => {
        document.getElementById("autogen_search_anchor").href =  "#"+document.getElementById("autogen_search_input").value;
        document.getElementById("autogen_search_input").addEventListener("keyup", function(e) {
              if (e.keyCode == 13) {document.getElementById('autogen_search_anchor').click();}
        });
        }, 400);

    </script>
    """)

    file.write('</ul><hr>')

    object_list = list(dir(module))
    object_list.sort()

    if '__docs_excludes__' in object_list:
        exclude_list = eval('module.__docs_excludes__')
    else:
        exclude_list = ()

    for object_name in object_list:
        #print(module.__name__, object_name)
        if not object_name.startswith('_') and  object_name not in exclude_list:
            object = eval('module.'+object_name)
            #check if is func or class
            if callable(object):
                #chekc if is native to module
                if object.__module__ == module.__name__:
                    if inspect.isclass(object):
                        write_class(object, object_name, file, template)
                    elif not inspect.isclass(object):
                        write_item(object, object_name, file, template)

    file.write(template[len(template)-2])

    file.close()
    print(os.listdir(file_path))
    os.chdir(prev_path)
