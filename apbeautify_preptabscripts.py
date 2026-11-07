import os, time, re, sys
from datetime import datetime
import argparse
from pathlib import Path






# class TableSplitter:
#     def __init__(self,data):
#         self.data = data
#         self.pos = None
#         self.start = None
#         self.need_reiterate = None
#         self.delimiter = r"^\s*?'{10}'*?\s*?\n\s*?'{3}[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n"

#     def find_next_delimniter_pos(self):
#         match = re.search(self.delimiter,self.data[self.pos:],flags=re.M|re.DOTALL|re.I)
#         if match:
#             return match.start(0) + self.pos
#         else:
#             return -1
#     def __iter__(self):
#         self.start = None
#         self.pos = self.find_next_delimniter_pos()
#         self.need_reiterate = 0
#         return self
#     def __next__(self):
#         if len(self.data)==0:
#             raise StopIteration
#         elif self.pos<0:
#             if self.start>=len(self.data):
#                 raise StopIteration
#             else:
#                 part = self.data[self.start:]
#                 self.start = len(self.data)
#                 return part
#         else:
#             part = self.data[self.start:self.pos]
#             matches_settable_pattern = re.findall(r"^\s*?set\b\s*?\btable\s*?=.*?",part,flags=re.M|re.DOTALL|re.I)
#             if not matches_settable_pattern:
#                 self.need_reiterate = 0
#             elif len(matches_settable_pattern)==1:
#                 self.need_reiterate = 0
#             elif len(matches_settable_pattern)>1:
#                 #the tricky one
#                 total_settable_pattern_counts = len(matches_settable_pattern)
#                 processed_settable_pattern_counts = self.need_reiterate
#                 if processed_settable_pattern_counts >= total_settable_pattern_counts:
#                     pass
#                 else:
#                     TBD...
#             else:
#                 raise AttributeError('what?')
#             self.start = self.pos
#             self.pos = self.find_next_delimiter_pos()
#             return part


class TableSplitter:
    def __init__(self,data):
        self.data = data
        self.delimiter = r"^\s*?'{10}'*?\s*?\n\s*?'{3}[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n"

    def __iter__(self):
        delimiters = re.finditer(self.delimiter,self.data,flags=re.M|re.DOTALL|re.I)
        delimiters = [ delim.start(0) for delim in delimiters ]
        parts = []
        start = 0
        for delim in delimiters:
            pos = delim
            parts.append(self.data[start:pos])
            start = pos
        parts.append(self.data[start:])
        return iter(parts)





def syntaxpreprocessor_table_reordergridsummarytablesummaryof(txt):
    def reorder(txt):
        parts = [ p.strip() for p in txt.split(',') ]
        parts.sort()
        return ','.join(parts)
    return re.sub(r'(\bgridsummary\w*\s*?\(\s*?\s*?tabledoc\s*?,\s*?"[^\n]*?\s*?,\s*?"\s*?\w+\s*?"s*?,\s*?")(\s*?\w+\s*?(?:\s*?,\s*?\w+\s*?)*?)(\s*?"[^\n]*?\))',lambda m:'{part1}{part2}{part3}'.format(part1=m[1],part2=reorder(m[2]),part3=m[3]),txt,flags=re.I)

def syntaxpreprocessor_table_normalizelinebreaks(txt):
    return re.sub(
        r'("!)(.*?)(!")',
        lambda m: '{opening}{content_escaped}{closingpart}'.format(opening=m[1],closingpart=m[3],content_escaped=re.sub(r'[\n]','\\\\n',m[2],flags=re.M|re.DOTALL|re.I)),
        re.sub(
            r"('!)(.*?)(!')",
            lambda m: '{opening}{content_escaped}{closingpart}'.format(opening=m[1],closingpart=m[3],content_escaped=re.sub(r'[\n]','\\\\n',m[2],flags=re.M|re.DOTALL|re.I)),
            txt,
            flags=re.M|re.DOTALL|re.I
        ),
        flags=re.M|re.DOTALL|re.I
    )


def syntaxextractor_title_comment(txt,fields):
    name = 'title_comment'
    matches = re.match(r"^\s*?'{10}'*?\s*?\n\s*?'{3}'*\s*([^\n]*?)\s*?\n\s*?'{10}'*?\s*?\n.*?$",txt,flags=re.M|re.DOTALL|re.I)
    result = None
    if matches:
        result = matches[1]
    return name,result

def syntaxextractor_comments(txt,fields):
    name = 'comments'
    matches = re.match(r"^(\s*?'{10}'*?\s*?\n\s*?'{3}'*\s*[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n)((?:\s*?'[^\n]*?\s*?\n)*)((?:\s*?[^\n]*?\s*?\n)*?)((?:\s*?set\b\s*?\btable\s*?=[^\n]*?\s*?\n)?)((?:\s*?[^\n]*?\s*?\n)*)$",txt,flags=re.M|re.DOTALL|re.I)
    result = None
    if matches:
        result = matches[2]
    return name,result

def syntaxextractor_tablecode(txt,fields):
    name = 'tablecode'
    matches = re.match(r"^(\s*?'{10}'*?\s*?\n\s*?'{3}'*\s*[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n)((?:\s*?'[^\n]*?\s*?\n)*)((?:\s*?[^\n]*?\s*?\n)*?)((?:\s*?set\b\s*?\btable\s*?=[^\n]*?\s*?\n)?)((?:\s*?[^\n]*?\s*?\n)*)$",txt,flags=re.M|re.DOTALL|re.I)
    result = None
    if matches:
        result = matches[4]
    return name,result

def syntaxextractor_tablecode_leadinglines(txt,fields):
    name = 'tablecode_leadinglines'
    matches = re.match(r"^(\s*?'{10}'*?\s*?\n\s*?'{3}'*\s*[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n)((?:\s*?'[^\n]*?\s*?\n)*)((?:\s*?[^\n]*?\s*?\n)*?)((?:\s*?set\b\s*?\btable\s*?=[^\n]*?\s*?\n)?)((?:\s*?[^\n]*?\s*?\n)*)$",txt,flags=re.M|re.DOTALL|re.I)
    result = None
    if matches:
        result = matches[3]
    return name,result

def syntaxextractor_tablecode_trailinglines(txt,fields):
    name = 'tablecode_trailinglines'
    matches = re.match(r"^(\s*?'{10}'*?\s*?\n\s*?'{3}'*\s*[^\n]*?\s*?\n\s*?'{10}'*?\s*?\n)((?:\s*?'[^\n]*?\s*?\n)*)((?:\s*?[^\n]*?\s*?\n)*?)((?:\s*?set\b\s*?\btable\s*?=[^\n]*?\s*?\n)?)((?:\s*?[^\n]*?\s*?\n)*)$",txt,flags=re.M|re.DOTALL|re.I)
    result = None
    if matches:
        result = matches[5]
    return name,result

def syntaxextractor_table_title(txt,fields):
    name = 'table_title'
    result = None
    matches = None
    if fields['tablecode']:
        matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?createtable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?creategridslicetable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?tabledoc.tables.addnew\s*?\(\s*?([^\s][^,]*?)\s*?,\s*?(([^\s].*?))\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?create\w*table\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if matches:
            result = matches[4]
    return name,result

def syntaxextractor_table_axis(txt,fields):
    name = 'table_axis'
    result = None
    matches = None
    if fields['tablecode']:
        matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?createtable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?creategridslicetable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?tabledoc.tables.addnew\s*?\(\s*?([^\s][^,]*?)\s*?,\s*?(([^\s].*?))\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?create\w*table\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if matches:
            result = matches[3]
    return name,result

def syntaxextractor_table_variable(txt,fields):
    name = 'table_variable'
    result = None
    matches = None
    if fields['tablecode']:
        matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?createtable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?creategridslicetable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?tabledoc.tables.addnew\s*?\(\s*?([^\s][^,]*?)\s*?,\s*?(([^\s].*?))\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?create\w*table\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if matches:
            result = matches[2]
    return name,result

def syntaxextractor_table_id(txt,fields):
    name = 'table_id'
    result = None
    matches = None
    if fields['tablecode']:
        matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?createtable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?creategridslicetable\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?tabledoc.tables.addnew\s*?\(\s*?([^\s][^,]*?)\s*?,\s*?(([^\s].*?))\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if not matches:
            matches = re.match(r"^\s*?set\b\s*?\btable\s*?=\s*?create\w*table\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?[^,]*?\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s][^,]*?)\s*?,\s*?([^\s].*?)\s*?,\s*?([^\s][^,]*?)\s*?\)\s*?(?:'[^\n]*?)?\s*?\n",fields['tablecode'],flags=re.M|re.DOTALL|re.I)
        if matches:
            result = matches[1]
    return name,result

def syntaxextractor_table_addedrules(txt,fields):
    name = 'table_addedrules'
    result = None
    if fields['tablecode_trailinglines']:
        lines = fields['tablecode_trailinglines'].split('\n')
        lines = [ line for line in lines if re.match(r'^\s*?table\..*?',line,flags=re.I) ]
        if len(lines)>0:
            result = '\n'.join(lines)
    return name,result

def syntaxextractor_table_filters(txt,fields):
    name = 'table_filters'
    result = None
    if fields['tablecode_trailinglines']:
        lines = fields['tablecode_trailinglines'].split('\n')
        lines = [ line for line in lines if re.match(r'^\s*?table\..*?',line,flags=re.I) ]
        lines_filters = []
        for line in lines:
            matches = re.match(r'^\s*?table\.filters\.addnew\s*?\(\s*?"[^"]*?"\s*?,\s*?([^\n]*?)\s*?,\s*?".*?"\s*?\)\s*?(?:\'[^\n]*?)?\s*?$',line,flags=re.I)
            if matches:
                lines_filters.append(matches[1])
        if len(lines_filters)>0:
            result = '\n'.join(lines_filters)
    return name,result





syntaxextractors = [
    syntaxextractor_title_comment,
    syntaxextractor_comments,
    syntaxextractor_tablecode,
    syntaxextractor_tablecode_leadinglines,
    syntaxextractor_tablecode_trailinglines,
    syntaxextractor_table_title,
    syntaxextractor_table_axis,
    syntaxextractor_table_id,
    syntaxextractor_table_addedrules,
    syntaxextractor_table_filters,
]

syntaxpreprocessors = [
    syntaxpreprocessor_table_normalizelinebreaks,
    syntaxpreprocessor_table_reordergridsummarytablesummaryof,
]



def compile_ultimate_table_id(table_def):
    result = table_def['table_id']
    if not result:
        result = table_def['title_comment']
    return result





def beautify(textfilecontents):
    column_specs = ['name','rawtextcontents']
    tables = []

    parts = TableSplitter(textfilecontents)
    table_number = 0
    table_last_variable = None
    for tabscript in parts:

        for syntaxpreprocessor in syntaxpreprocessors:
            tabscript = syntaxpreprocessor(tabscript)

        table_def_obj = {
            'rawtextcontents': tabscript
        }

        for syntaxparser in syntaxextractors:
            name,matching_piece = syntaxparser(tabscript,table_def_obj)
            table_def_obj = {**table_def_obj,**{name:matching_piece}}
            if not (name in column_specs):
                column_specs.append(name)

        # table_def_obj['name'] = table_def_obj['title_comment']
        table_def_obj['name'] = compile_ultimate_table_id(table_def_obj)
        if not table_def_obj['title_comment'] and (table_number==0):
            # table_def_obj['name'] = 'preparation_code'
            table_def_obj['name'] = ''
        else:
            table_def_obj['table_number'] = table_number + 1
            table_number = table_number + 1

        table_scripts_clean = table_def_obj['rawtextcontents']
        if not table_def_obj['table_id'] and not table_def_obj['table_title'] and (table_def_obj['name']==''):
            # entry lines
            lines = table_scripts_clean.split('\n')
            variable = ''
            lines_updated = []
            for line in lines:
                line_updated = line
                if re.match(r'^\s*?\'+\s*?Variable\s*?:\s*?(\w.*?)\s*?$',line,flags=re.I|re.DOTALL):
                    matches = re.match(r'^\s*?\'+\s*?Variable\s*?:\s*?(\w.*?)\s*?$',line,flags=re.I|re.DOTALL)
                    variable = matches[1]
                    pass
                elif re.match(r'^\s*?\'+\s*?(\w[^\n]*?)\s*?-\s*?"[^\n]*?"\s*?>\s*?"([^\n]*?)\s*?"\s*?$',line,flags=re.I|re.DOTALL):
                    matches = re.match(r'^\s*?\'+\s*?(\w[^\n]*?)\s*?-\s*?"[^\n]*?"\s*?>\s*?"([^\n]*?)\s*?"\s*?$',line,flags=re.I|re.DOTALL)
                    line_updated = '\'' + line + '\n' + 'metadoc.fields["{variable}"].categories["{category}"].label = "{newlabel}"'.format(variable=variable,category=matches[1],newlabel=matches[2])
                lines_updated.append(line_updated)
            table_scripts_clean = '\n'.join(lines_updated)
        else:
            table_scripts_clean = '\n' + table_scripts_clean + '\n'

            # axis on a separate line, better for handling syntax with automations, when table syntax takes exactly 1 line
            comment = r'axis on a separate line, better for handling syntax with automations, when table syntax takes exactly 1 line'
            pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?\w+\s*?\(.*?\s*?,\s*?)("!.*?!")(\s*?,\s*?".*?\s*?"\s*?\))\s*?\n'
            if not re.search(pattern_search,table_scripts_clean,flags=re.I|re.DOTALL):
                pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?CreateGridSliceTable\s*?\(\s*?logme\s*?,\s*?tabledoc\s*?,\s*?bannernumber\s*?,\s*?[^,]*?\s*?,\s*?[^,]*?\s*?,\s*?[^,]*?\s*?,\s*?[^,]*?\s*?,\s*?)(.*?)\s*?(,\s*?"[^"]*?(?:"\s*?\+[^",]*?\s*?\+\s*?"[^"]*?)*?"\s*?\))\s*?\n'
            if not re.search(pattern_search,table_scripts_clean,flags=re.I|re.DOTALL):
                pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?\w+\s*?\(\s*?logme\s*?,\s*?tabledoc\s*?,\s*?bannernumber\s*?,\s*?[^,]*?\s*?,\s*?[^,]*?\s*?,\s*?)(.*?)\s*?(,\s*?"[^"]*?(?:"\s*?\+[^",]*?\s*?\+\s*?"[^"]*?)*?"\s*?\))\s*?\n'
            if not re.search(pattern_search,table_scripts_clean,flags=re.I|re.DOTALL):
                pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?tabledoc.tables.addnew\s*?\(\s*?[^,]*?\s*?,\s*?[^,]*?\s*?,\s*?)(.*?)\s*?(,\s*?"[^"]*?(?:"\s*?\+[^",]*?\s*?\+\s*?"[^"]*?)*?"\s*?\))\s*?\n'
            pattern_replacement = r'\n$1axis = $3\n$1$2axis$4\n'
            #table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)
            if not re.search(r'\baxis\s*?=\s*?""\s*?\n',re.sub(pattern_search,lambda m: '\n'+m[1]+'axis = '+re.sub(r'\\n','\n',m[3])+'\n'+m[1]+m[2]+'axis'+m[4]+'\n',table_scripts_clean,flags=re.I|re.DOTALL),flags=re.I|re.DOTALL):
                table_scripts_clean = re.sub(pattern_search,lambda m: '\n'+m[1]+'axis = '+re.sub(r'\\n','\n',m[3])+'\n'+m[1]+m[2]+'axis'+m[4]+'\n',table_scripts_clean,flags=re.I|re.DOTALL)

            # fix ",axis"
            comment = r'fix ",axis"'
            pattern_search = r',\baxis\b'
            pattern_replacement = r', axis'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # grid slice, totally hate it, I don't know why do we need a separate function, why we can't just use CreateTable(); will turn it to normal CreateTable() where possible; please process "axis on a separate line" first, if it has multi-line axes
            comment = r'grid slice, totally hate it, I don\'t know why do we need a separate function, why we can\'t just use CreateTable(); will turn it to normal CreateTable() where possible; please process "axis on a separate line" first, if it has multi-line axes'
            pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?)CreateGridSliceTable\s*?(\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?bannernumber\s*?,\s*?[^\n,]*?\s*?,\s*?"[^\n,]*?)"\s*?,\s*?"\s*?\{\s*?("\s*\+\s*?[^\n,]*?\+\s*?")\s*?\}\s*?"\s*?,\s*?"\s*?(\w+\s*?"\s*?,\s*?.*?\s*?,\s*?".*?"\s*?\))\s*?\n'
            pattern_replacement = r'\n$1$2CreateTable$3[{$4}].$5\n'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # bring summary table definitions to a separate line, I like it more, it is easier to find visually and to edit
            comment = r'bring summary table definitions to a separate line, I like it more, it is easier to find visually and to edit'
            pattern_search = r'\n(\s*?)(set\b\s*?\btable\s*?=\s*?\w+\s*?\(\s*?\w+\s*?,\s*?\w+\s*?,\s*?bannernumber\s*?,\s*?[^\n,]*?\s*?,\s*?"[^\n]*?"\s*?,\s*?)(?:\s*?""\s*?\+\s*?)?(\w+\s*?\(.*?\))\s*?(?:\s*?\+\s*?"")?\s*?(\s*?,\s*?".*?"\s*?\))\s*?\n'
            pattern_replacement = r'\n$1axis = $3\n$1$2axis$4\n$1\'table.filters.addnew("fauto",GetAutoFilterGrid(TableDoc,"VARIABLE","GV")," ")\n'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # and fix the "VARIABLE" part in GetAutoFilterGrid, added with previous replacement
            comment = r'and fix the "VARIABLE" part in GetAutoFilterGrid, added with previous replacement'
            pattern_search = r'\n(\s*?(?:\'\s*?)*?\s*?axis\s*?=\s*?\w+\s*?\(\s*?tabledoc\s*?,\s*?"\s*?(\w+)\s*?"\s*?,.*?\)\s*?\n\s*?(?:\'\s*?)*?\s*?set\b\s*?\btable\s*?=.*?\s*?\n\s*?(?:\'\s*?)*?\s*?table\.filters\.addnew\s*?\(\s*?"\s*?\w+\s*?"\s*?,\s*?getautofiltergrid\s*?\(\s*?\w+\s*?,\s*?")\s*?(\w+)\s*?("\s*?,\s*?".*?"\s*?\)\s*?,\s*?".*?"\s*?\)\s*?\n)'
            pattern_replacement = r'\n$1$2$4'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # bases for gridsummarybase where missing, where individual bases are hidden and any total bases is not added either
            comment = r'bases for gridsummarybase where missing, where individual bases are hidden and any total bases is not added either'
            pattern_search = r'\n(\s*?(?:\'\s*?)*?\s*?axis\s*?=\s*?(?:\s*?""\s*?\+\s*?)?\w+\s*?\(\s*?.*?\s*?,\s*?")("\s*?,\s*?"\s*?true\s*?"\s*?\)\s*?(?:\s*?\+\s*?"")?\s*?\n)'
            pattern_replacement = r'\n$1"+iif(APPLY_WEIGHT,"unweightedbase(), ","")+"base(),$2'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # get rid of stupid getlabel() in table titles
            comment = r'get rid of stupid getlabel() in table titles'
            pattern_search = r'\n(\s*?set\b\s*?\btable\s*?=\s*?\w+\s*?\(.*?\s*?,\s*?".*?"\s*?\+\s*?)getlabel\s*?\(\s*?([^\n,]*?)\s*?\)(\s*?\+\s*?".*?\s*?"\s*?\)\s*?\n)'
            pattern_replacement = r'\n$1$2.label$3'
            table_scripts_clean = re.sub(pattern_search,re.sub(r'\$([0-9])',r'\\\1',pattern_replacement),table_scripts_clean,flags=re.I|re.DOTALL)

            # and stupid trailing whitespaces
            table_scripts_clean = re.sub(r'([^\s])\s*?\n',r'\1'+'\n',table_scripts_clean,flags=re.I|re.DOTALL)

            if 'table_variable' not in table_def_obj:
                table_def_obj['table_variable'] = None # TODO: implement
            if table_last_variable is not None and table_def_obj['table_variable'] is not None and table_last_variable==table_def_obj['table_variable']:
                table_scripts_clean = '\'<<SAME VARIABLE>>'
            table_last_variable = table_def_obj['table_variable']

        tables.append(table_scripts_clean)

    return '\n'.join(tables)





def beautify_working_file(*args):
    raise Exception('You crazy do it yourself this is not implemented here')




def main(args):
    start_time = datetime.utcnow()
    char_endl = ""
    print("Starting...")
    
    inp_file_specs_name = None
    if args.da:
        inp_file_specs_name = Path(args.da)
    inp_file_working_name = None
    if args.prep:
        inp_file_working_name = Path(args.prep)
    
    inp_file_specs = open(inp_file_specs_name, encoding="utf8")
    
    print("Reading file...")
    contents_specs = inp_file_specs.read()
    
    if inp_file_working_name:
        inp_file_working = open(inp_file_working_name, encoding="utf8")
        contents_working = inp_file_working.read()
        inp_file_working = None
    
    inp_file_specs = None
    
    print("Replacements...")
    contents_specs = beautify(contents_specs)
    
    if inp_file_working_name:
        print("Replacements on working file...")
        contents_working = beautify_working_file(contents_working)
    
    print("Writing results...")
    out_file_specs_name = '{prev_name}{added_part}'.format(prev_name=inp_file_specs_name,added_part='.f.mrs')
    with open(out_file_specs_name,'w', encoding="utf8") as out_file_specs:
        out_file_specs.write(contents_specs)
    
    if inp_file_working_name:
        print("Writing results to working file...")
        out_file_working_name = '{prev_name}{added_part}'.format(prev_name=inp_file_working_name,added_part='.upd.mrs')
        with open(out_file_working_name,'w', encoding="utf8") as out_file_working:
            out_file_working.write(contents_working)
    
    end_time = datetime.utcnow()
    #elapsed_time = end_time - start_time
    print("Finished") # + str(elapsed_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Beautify dms"
    )
    parser.add_argument(
        '-1',
        '--da',
        metavar='PrepDataDMS.mrs',
        help='DA DMS Exports',
        required=True
    )
    parser.add_argument(
        '-2',
        '--prep',
        metavar='D_Prep.dms',
        help='PrepData script',
        required=False
    )
    args = parser.parse_args()
    main(args)
