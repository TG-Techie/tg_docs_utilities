import os, time, shutil, inspect

#order style, function, class, class_function, file_start, file_end
default_template = [
#style part of string
'''
body{background-color: white;}
''',
#wrapper for a function
'''<hr><div>
    <h3>{{name}}</h3>
    <p>{{content}}</p>
</div>
''',
#wrapper for a class
'''
<hr><div>
    <h3>{{name}}</h3>
    <p>{{content}}</p>
</div>
''',
#wrapper for a method of a class
'''
<hr><div>
    <h3>{{name}}</h3>
    <p>{{content}}</p>
</div>
''',
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
<!--/ul--></body></html>''',
]
default_template.append(default_template[1])

def parse_docstring(object, object_name, template):

    section = template

    doc = str(object.__doc__).split(':param ')
    val = doc.pop(0)
    if val == 'None':
        doc_out = '<em>No documentation provided.</em>'
    else:
        doc_out = val

    input_parens = '('
    for line in doc:
        input_parens += line.split(':')[0] +',  '
    input_parens += '):'

    section = section.replace('{{name}}',object_name+input_parens)

    if len(doc):
        doc_out +='<ul> <h4>Input'+('s','')[len(doc) == 1]+':</h4>'
        while len(doc):
            doc_out += '<li>'
            doc_out += doc.pop(0).strip('\n')
            doc_out += '</li>\n'
        doc_out += '</ul>'

    return(section.replace('{{content}}',doc_out))

def write_function(func, func_name, file, template, index = 1):
    string = parse_docstring(func, func_name, template[index])
    #print()
    #print(func_name, '"'+string+'"')
    if len(string):
        file.write(string+'\n')

def write_class(class_obj, class_name, file, template):

    attr_list = list(dir(class_obj))
    attr_list.sort()

    if '__init__' in attr_list:
        file.write(parse_docstring(eval('class_obj.__init__') ,class_name, template[2]))
    else:
        file.write(parse_docstring(class_obj, class_name, template[2]))

    file.write('<ul>')

    for attribute_name in attr_list:
        attribute = eval('class_obj.'+attribute_name)
        if not attribute_name[0] == '_':
            if callable(attribute) :
                file.write('<li>')
                write_function(attribute, class_name+'.'+attribute.__name__, file, template, index = 3)
                file.write('</li>')

    file.write('</ul>')

def compile_page(module, output_path, template = default_template, layout = None):
    print()
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

    file.write(template[4].replace('{{style}}',template[0]).replace('{{title}}',file_title))

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
                        write_function(object, object_name, file, template)

    file.write(template[5])

    file.close()
    print(os.listdir(file_path))
    os.chdir(prev_path)
