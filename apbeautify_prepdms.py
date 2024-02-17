import os, time, re, sys
from datetime import datetime
import argparse
from pathlib import Path

re_patter_matching_metadata = r'^(\s*?(?:\s*?\'[^\n]*?\s*?\n)*?\s*?Metadata[^\n]*?\s*?\n)(.*?\s*?\n)\s*?(End\b\s+\bMetadata\b\s*?(?:\'[^\n]*?)?\s*?\n.*?)$'

re_patter_matching_onnextcase = r'^(.*?Event\s*?\(\s*?OnNextCase\s*?\)\s*?\n)(.*?\s*?\n?)\s*?(\bEnd\b\s+\bEvent\b\s*?\n?\s*?)$'

stored_global_dict_of_vars_from_specs = []

def confirm_trailing_linebreak(t):
    return re.sub(
        r'^(.*?)((?:\n)?)$',
        lambda matches_linebreak: '{body}{linebreak}'.format(
            body = matches_linebreak[1],
            linebreak = "\n"
        ),
        t,
        flags = re.DOTALL|re.ASCII|re.I
    )

def trim_linebreaks(t):
    return confirm_trailing_linebreak( re.sub(
        r'^(?:\s*?\n)*',
		'',
		re.sub(
            r'\s*?\n(\s*?\n)*\s*$',
		    '',
		    t,
		    flags = re.DOTALL|re.ASCII|re.I
        ),
		flags = re.DOTALL|re.ASCII|re.I
    ) )

def split_linebreaks(t):
    return [
        trim_linebreaks(item) for item in re.split(
            r'\s*?\n(?:\s*?\n)+',
            t,
            flags = re.DOTALL|re.ASCII|re.I
        )
    ];

def tempprintformat(t,chars=20):
    t = re.sub(r'\n',' ',t,flags=re.DOTALL|re.ASCII|re.I)
    return '{begin}...{end}'.format(begin=t[:chars],end=t[-chars:])

def beautify_metadata(t):
    print('beautify_metadata called!')
    
    print_each_verbose = False
    
    def process_part(t):
        def split_categories_text(t):
            results = []
            goon = True
            while goon:
                s = re.search(r'^(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,\s*?\n)(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?\s*?\n)(.*?)$', t, flags=re.DOTALL|re.ASCII|re.I)
                if s:
                    results.append(re.sub(r'\n',' ',s[1],flags=re.DOTALL|re.ASCII|re.I))
                    t = '{t2}{trest}'.format(t2 = s[2],trest = s[3])
                    goon = True
                else:
                    goon = False
            results.append(re.sub(r'\n',' ',t,flags=re.DOTALL|re.ASCII|re.I))
            return results
        def split_categories(t):
            results = split_categories_text(t)
            results = [ re.search(r'^\s*?(\w+)\s*?((?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,?\s*?$',line,flags=re.DOTALL|re.ASCII|re.I) for line in results ]
            results = [ { 'name': s[1], 'label': re.sub(r'^\s*?"?\s*?(.*?)\s*?"?\s*?$',lambda m: m[1],s[2]), 'full_description': s[0] } for s in results ]
            return results
        def split_categories_comment(t):
            #results = re.split(r'\n',t,flags=re.DOTALL|re.ASCII|re.I)
            results = t
            results = [ re.search(r'^\s*?\'*?\s*?(\w+)\s*?"\s*?([^\n]*?)\s*?"\s*?expression\s*?\(\s*?"\s*?([^\n]*?)\s*?"\s*?\)\s*?,?\s*?$',line,flags=re.DOTALL|re.ASCII|re.I) for line in results ]
            results = [ { 'name': s[1], 'label': s[2], 'logic': s[3], 'full_description': s[0] } for s in results ]
            return results
        def find_matching_logic_from_comment_stub(name,stubs_comm):
            matching = list( filter( lambda stub: stub['name'].lower()==name.lower(), stubs_comm ) )
            if len(matching)>0:
                return matching[0]['logic']
            else:
                return None
        
        if print_each_verbose:
            print('')
        s = re.search( r'^((?:\s*?\'[^\n]*?\s*?\n)*)(.*?\n)((?:\s*?\'[^\n]*?\s*?\n)*)$', t, flags=re.DOTALL|re.ASCII|re.I )
        q_comments_global = list( filter( lambda t: not re.search(r'^\s*?$',t,flags=re.DOTALL|re.ASCII|re.I), [ '{body}'.format(body=re.sub(r'^\s*\'\s*(.*?)\s*?$',lambda m: m[1],line,flags=re.DOTALL|re.ASCII|re.I)) for line in re.split(r'\n', re.sub(r'\n$','',s[1]), flags=re.DOTALL|re.ASCII|re.I) ] ) )
        q_body = s[2]
        q_comments_after = list( filter( lambda t: not re.search(r'^\s*?$',t,flags=re.DOTALL|re.ASCII|re.I), [ '{body}'.format(body=re.sub(r'^\s*\'\s*(.*?)\s*?$',lambda m: m[1],line,flags=re.DOTALL|re.ASCII|re.I)) for line in re.split(r'\n', re.sub(r'\n$','',s[3]), flags=re.DOTALL|re.ASCII|re.I) ] ) )
        s = re.search(r'^(\s*?)(\w+)\s*?"\s*?([^\n]*?)\s*?"',q_body,flags=re.DOTALL|re.ASCII|re.I)
        if not s:
            s = re.search(r'^(\s*?)(\w+)\s*?(.*?)',q_body,flags=re.DOTALL|re.ASCII|re.I)
        q_indent = "\t"
        q_name = None
        q_label = ''
        if not s:
            pass
        else:
            q_indent = s[1]
            q_name = s[2]
            q_label = s[3]
        s = re.search(r'^(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?[^\n]*?\s*?(?:\s*?\[.*?\])?\s*?\n?\s*?categorical\s*?(?:\[\s*?[^\n]*?\s*?\])?\s*?\n?\s*?\{\s*?\n?\s*?)((?:\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,?\s*?\n)*)(\}.*?;.*?)$',q_body,flags=re.DOTALL|re.ASCII|re.I)
        q_is_categorical = not not s
        q_is_banner = not not re.search(r'\s*?\w*banner\w*\s*?',q_name,flags=re.DOTALL|re.ASCII|re.I)
        if q_is_categorical:
            q_categorical_beginning = s[1]
            q_categorical_stubs = split_categories(s[2])
            q_categorical_end = s[3]
            if q_is_banner:
                q_categorical_end = re.sub(r'^(\s*?\})(.*?)$',lambda m: '{begin}{ins}{end}'.format(begin=m[1],end=m[2],ins=' axis("{..,unweightedbase() [IsHidden=True], base() [IsHidden=True]}")'),q_categorical_end,flags=re.DOTALL|re.ASCII|re.I)
            q_categorical_comments_stubs = split_categories_comment(q_comments_after)
            q_categorical_stubs_matched_from_comments = [ {**stub,**({'logic':find_matching_logic_from_comment_stub(stub['name'],q_categorical_comments_stubs)})} for stub in q_categorical_stubs ]
            q_categorical_stubs_matched_from_comments = [ {**stub,**({'needcomma':True})} for stub in q_categorical_stubs_matched_from_comments ]
            q_categorical_stubs_matched_from_comments[len(q_categorical_stubs_matched_from_comments)-1]['needcomma'] = False
            q_categorical_stubs_updsyntax = ''.join( [ '{indentmain}{indentadded}{name} "{label}"{expressionpart}{comma}{linebreak}'.format(indentmain=q_indent,indentadded="\t",name=stub['name'],label=re.sub(r'\n',' ',re.sub(r'"','""',stub['label'],flags=re.DOTALL|re.ASCII|re.I),flags=re.DOTALL|re.ASCII|re.I),comma=(',' if stub['needcomma'] else ''),linebreak="\n",expressionpart=((' expression("{expr}")'.format(expr=re.sub(r'\n',' ',re.sub(r'"','""',stub['logic'],flags=re.DOTALL|re.ASCII|re.I),flags=re.DOTALL|re.ASCII|re.I))) if stub['logic'] else '')) for stub in q_categorical_stubs_matched_from_comments ] )
        if print_each_verbose:
            print('part: {desc}'.format(desc=q_name))
            if not q_name:
                if print_each_verbose:
                    print('{warning} part can\'t be parsed for name and label! "{example}"'.format(warning='WARNING!: ',example=tempprintformat(t,chars=40)))
            if len(q_comments_global)==0:
                if print_each_verbose:
                    print('{warning} part does not start with a comment! "{example}"'.format(warning='WARNING!: ',example=tempprintformat(t,chars=40)))
            print('content: {desc}'.format(desc=tempprintformat(q_body,chars=40)))
            t_debug = [ print('comment: {comment}'.format(comment=line)) for line in q_comments_global ]
            t_debug = [ print('comment after: {comment}'.format(comment=line)) for line in q_comments_after ]
            print('is_banner: {really}'.format(really = 'true' if q_is_banner else 'false' ))
            print('is_categorical: {really}'.format(really = 'true' if q_is_categorical else 'false' ))
            if q_is_categorical:
                for stub in q_categorical_stubs:
                    print('stub: {stub}'.format(stub = stub))
                for stub in q_categorical_comments_stubs:
                    print('comment stub: {stub}'.format(stub = stub))
                for stub in q_categorical_stubs_matched_from_comments:
                    print('final updated stub: {stub}'.format(stub = stub))
        dict_add = {}
        dict_add['q_comments_global'] = q_comments_global
        dict_add['q_body'] = q_body
        dict_add['q_comments_after'] = q_comments_after
        dict_add['q_indent'] = q_indent
        dict_add['q_name'] = q_name
        dict_add['q_label'] = q_label
        dict_add['q_indent'] = q_indent
        dict_add['q_name'] = q_name
        dict_add['q_label'] = q_label
        dict_add['q_is_categorical'] = q_is_categorical
        dict_add['q_is_banner'] = q_is_banner
        if q_is_categorical:
            dict_add['q_comments_global'] = q_comments_global
            dict_add['q_body'] = q_body
            dict_add['q_comments_after'] = q_comments_after
            dict_add['q_indent'] = q_indent
            dict_add['q_name'] = q_name
            dict_add['q_label'] = q_label
            dict_add['q_indent'] = q_indent
            dict_add['q_name'] = q_name
            dict_add['q_label'] = q_label
            dict_add['q_is_categorical'] = q_is_categorical
            dict_add['q_is_banner'] = q_is_banner
            dict_add['q_categorical_beginning'] = q_categorical_beginning
            dict_add['q_categorical_stubs'] = q_categorical_stubs
            dict_add['q_categorical_end'] = q_categorical_end
            dict_add['q_categorical_end'] = q_categorical_end
            dict_add['q_categorical_comments_stubs'] = q_categorical_comments_stubs
            dict_add['q_categorical_stubs_matched_from_comments'] = q_categorical_stubs_matched_from_comments
            dict_add['q_categorical_stubs_matched_from_comments'] = q_categorical_stubs_matched_from_comments
            dict_add['q_categorical_stubs_updsyntax'] = q_categorical_stubs_updsyntax
        stored_global_dict_of_vars_from_specs.append(dict_add)
        if q_is_categorical:
            return '{partcomments}{partbegin}{partstubs}{partend}'.format(partcomments='\n'.join([ '{indent}\'{line}{linebreak}'.format(indent=q_indent,line=line,linebreak="\n") for line in q_comments_global]),partbegin=q_categorical_beginning,partstubs=q_categorical_stubs_updsyntax,partend=q_categorical_end)
        else:
            return '{partcomments}{partbegin}{partstubs}{partend}'.format(partcomments='\n'.join([ '{indent}\'{line}{linebreak}'.format(indent=q_indent,line=line,linebreak="\n") for line in q_comments_global]),partbegin='',partstubs=q_body,partend='')
            
    
    t_parts = split_linebreaks(trim_linebreaks(t))
    #t_debug = [ print('part: "{part}"'.format(part=tempprintformat(t,chars=45))) for t in t_parts ]
    t_parts_processed = [ process_part(part) for part in t_parts ]
    t_clean = "\n" + ("\n\n\n".join(t_parts_processed)) + "\n"
    return t_clean
    #return "beautiful meta!"

def beautify_onnextcase(t):
    print('beautify_onnextcase called!')
    #def confirm_starting_with_comment(t):
    #    s = re.search( r'^\s*?\'[^\n]*?\s*?\n', t, flags = re.DOTALL|re.ASCII|re.I )
    #    if not s:
    #        print('{warning} part does not start with a comment! "{example}"'.format(warning='WARNING!: ',example=tempprintformat(t,chars=40)))
    t = re.sub( r'\s*?\n(?:\s*?\n)*(\s*?)((?:end if|next))', lambda m: '{lastlinebreak}{indent}{text}'.format(lastlinebreak="\n",indent=m[1],text=m[2]), t, flags = re.DOTALL|re.ASCII|re.I )
    t_parts = split_linebreaks(trim_linebreaks(t))
    #t_debug = [ print('part: "{part}"'.format(part=tempprintformat(t,chars=45))) for t in t_parts ]
    #t_debug = [ confirm_starting_with_comment(t) for t in t_parts ]
    t_clean = "\t\n" + ("\t\n\t\n\t\n".join(t_parts)) + "\t\n"
    return t_clean
    #return "beautiful onnextcase!"




def beautify_working_metadata(t):
    print('beautify_metadata called!')
    
    print_each_verbose = False
    
    def process_part(t_input):
        t = t_input
        def split_categories_text(t):
            results = []
            goon = True
            while goon:
                s = re.search(r'^(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,\s*?\n)(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?\s*?\n)(.*?)$', t, flags=re.DOTALL|re.ASCII|re.I)
                if s:
                    results.append(re.sub(r'\n',' ',s[1],flags=re.DOTALL|re.ASCII|re.I))
                    t = '{t2}{trest}'.format(t2 = s[2],trest = s[3])
                    goon = True
                else:
                    goon = False
            results.append(re.sub(r'\n',' ',t,flags=re.DOTALL|re.ASCII|re.I))
            return results
        def split_categories(t):
            results = split_categories_text(t)
            results = [ re.search(r'^\s*?(\w+)\s*?((?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,?\s*?$',line,flags=re.DOTALL|re.ASCII|re.I) for line in results ]
            results = [ { 'name': s[1], 'label': re.sub(r'^\s*?"?\s*?(.*?)\s*?"?\s*?$',lambda m: m[1],s[2]), 'full_description': s[0] } for s in results ]
            return results
        def split_categories_comment(t):
            #results = re.split(r'\n',t,flags=re.DOTALL|re.ASCII|re.I)
            results = t
            results = [ re.search(r'^\s*?\'*?\s*?(\w+)\s*?"\s*?([^\n]*?)\s*?"\s*?expression\s*?\(\s*?"\s*?([^\n]*?)\s*?"\s*?\)\s*?,?\s*?$',line,flags=re.DOTALL|re.ASCII|re.I) for line in results ]
            results = [ { 'name': s[1], 'label': s[2], 'logic': s[3], 'full_description': s[0] } for s in results ]
            return results
        def find_matching_logic_from_comment_stub(name,stubs_comm):
            matching = list( filter( lambda stub: stub['name'].lower()==name.lower(), stubs_comm ) )
            if len(matching)>0:
                return matching[0]['logic']
            else:
                return None
        
        if print_each_verbose:
            print('')
        s = re.search( r'^((?:\s*?\'[^\n]*?\s*?\n)*)(.*?\n)((?:\s*?\'[^\n]*?\s*?\n)*)$', t, flags=re.DOTALL|re.ASCII|re.I )
        q_comments_global = list( filter( lambda t: not re.search(r'^\s*?$',t,flags=re.DOTALL|re.ASCII|re.I), [ '{body}'.format(body=re.sub(r'^\s*\'\s*(.*?)\s*?$',lambda m: m[1],line,flags=re.DOTALL|re.ASCII|re.I)) for line in re.split(r'\n', re.sub(r'\n$','',s[1]), flags=re.DOTALL|re.ASCII|re.I) ] ) )
        q_body = s[2]
        q_comments_after = list( filter( lambda t: not re.search(r'^\s*?$',t,flags=re.DOTALL|re.ASCII|re.I), [ '{body}'.format(body=re.sub(r'^\s*\'\s*(.*?)\s*?$',lambda m: m[1],line,flags=re.DOTALL|re.ASCII|re.I)) for line in re.split(r'\n', re.sub(r'\n$','',s[3]), flags=re.DOTALL|re.ASCII|re.I) ] ) )
        s = re.search(r'^(\s*?)(\w+)\s*?"\s*?([^\n]*?)\s*?"',q_body,flags=re.DOTALL|re.ASCII|re.I)
        if not s:
            s = re.search(r'^(\s*?)(\w+)\s*?(.*?)',q_body,flags=re.DOTALL|re.ASCII|re.I)
        q_indent = "\t"
        q_name = None
        q_label = ''
        q_is_categorical = None
        if not s:
            pass
        else:
            q_indent = s[1]
            q_name = s[2]
            q_label = s[3]
        #print('DEBUG: q_name == "{q_name}", all = "{all}"'.format(q_name=q_name,all=tempprintformat(t_input,chars=40)))
        if not not q_name:
            s = re.search(r'^(\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?[^\n]*?\s*?(?:\s*?\[.*?\])?\s*?\n?\s*?categorical\s*?(?:\[\s*?[^\n]*?\s*?\])?\s*?\n?\s*?\{\s*?\n?\s*?)((?:\s*?\w+\s*?(?:(?:".*?")|\-|)\s*?(?:\s*?expression\s*?\(\s*?"[^\n]*?\s*?"\s*?\)\s*?)?\s*?(?:\s*?\[.*?\])?\s*?(?:\s+(?:fix|other|exclusive|ran|canfilter|nofilter|na|other|other\b\s*?\buse\s*?\([^\n]*?))*\s*?,?\s*?\n)*)(\}.*?;.*?)$',q_body,flags=re.DOTALL|re.ASCII|re.I)
            q_is_categorical = not not s
            q_is_banner = not not re.search(r'\s*?\w*banner\w*\s*?',q_name,flags=re.DOTALL|re.ASCII|re.I)
            if q_is_categorical:
                q_categorical_beginning = s[1]
                q_categorical_stubs = split_categories(s[2])
                q_categorical_end = s[3]
                if q_is_banner:
                    q_categorical_end = re.sub(r'^(\s*?\})(.*?)$',lambda m: '{begin}{ins}{end}'.format(begin=m[1],end=m[2],ins=' axis("{..,unweightedbase() [IsHidden=True], base() [IsHidden=True]}")'),q_categorical_end,flags=re.DOTALL|re.ASCII|re.I)
                q_categorical_comments_stubs = split_categories_comment(q_comments_after)
                q_categorical_stubs_matched_from_comments = [ {**stub,**({'logic':find_matching_logic_from_comment_stub(stub['name'],q_categorical_comments_stubs)})} for stub in q_categorical_stubs ]
                q_categorical_stubs_matched_from_comments = [ {**stub,**({'needcomma':True})} for stub in q_categorical_stubs_matched_from_comments ]
                q_categorical_stubs_matched_from_comments[len(q_categorical_stubs_matched_from_comments)-1]['needcomma'] = False
                q_categorical_stubs_updsyntax = ''.join( [ '{indentmain}{indentadded}{name} "{label}"{expressionpart}{comma}{linebreak}'.format(indentmain=q_indent,indentadded="\t",name=stub['name'],label=re.sub(r'\n',' ',re.sub(r'"','""',stub['label'],flags=re.DOTALL|re.ASCII|re.I),flags=re.DOTALL|re.ASCII|re.I),comma=(',' if stub['needcomma'] else ''),linebreak="\n",expressionpart=((' expression("{expr}")'.format(expr=re.sub(r'\n',' ',re.sub(r'"','""',stub['logic'],flags=re.DOTALL|re.ASCII|re.I),flags=re.DOTALL|re.ASCII|re.I))) if stub['logic'] else '')) for stub in q_categorical_stubs_matched_from_comments ] )
        if print_each_verbose:
            print('part: {desc}'.format(desc=q_name))
            if not q_name:
                if print_each_verbose:
                    print('{warning} part can\'t be parsed for name and label! "{example}"'.format(warning='WARNING!: ',example=tempprintformat(t,chars=40)))
            if len(q_comments_global)==0:
                if print_each_verbose:
                    print('{warning} part does not start with a comment! "{example}"'.format(warning='WARNING!: ',example=tempprintformat(t,chars=40)))
            print('content: {desc}'.format(desc=tempprintformat(q_body,chars=40)))
            t_debug = [ print('comment: {comment}'.format(comment=line)) for line in q_comments_global ]
            t_debug = [ print('comment after: {comment}'.format(comment=line)) for line in q_comments_after ]
            print('is_banner: {really}'.format(really = 'true' if q_is_banner else 'false' ))
            print('is_categorical: {really}'.format(really = 'true' if q_is_categorical else 'false' ))
            if q_is_categorical:
                for stub in q_categorical_stubs:
                    print('stub: {stub}'.format(stub = stub))
                for stub in q_categorical_comments_stubs:
                    print('comment stub: {stub}'.format(stub = stub))
                for stub in q_categorical_stubs_matched_from_comments:
                    print('final updated stub: {stub}'.format(stub = stub))
        def is_name_matching(q):
            if q['q_name'].lower()==q_name.lower():
                return True
            if q_is_banner:
                q_this_name_clean = re.sub(r'^\s*?DV_(\w+)\s*?$',lambda m: m[1],q_name,flags=re.DOTALL|re.ASCII|re.I)
                q_cmp_name_clean = re.sub(r'^\s*?DV_(\w+)\s*?$',lambda m: m[1],q['q_name'],flags=re.DOTALL|re.ASCII|re.I)
                if q_this_name_clean.lower()==q_cmp_name_clean.lower():
                    return True
            return False
        matching_var_from_specs = None
        if not not q_name:
            matching_vars_from_specs = list( filter( is_name_matching, stored_global_dict_of_vars_from_specs ) )
            matching_var_from_specs = None
            if len(matching_vars_from_specs)>0:
                matching_var_from_specs = matching_vars_from_specs[0]
            print('DEBUG: q_name == "{q_name}", matching = "{matching}", q_is_categorical = "{q_is_categorical}", all = "{all}"'.format(q_name=q_name,q_is_categorical=('yes' if q_is_categorical else '-'),all=tempprintformat(t_input,chars=40),matching=(matching_var_from_specs['q_name'] if matching_var_from_specs else '-')))
        if q_is_categorical and matching_var_from_specs:
            q_categorical_stubs_updfrommatching = matching_var_from_specs['q_categorical_stubs_updsyntax']
            return '{partcomments}{partbegin}{partstubs}{partend}'.format(partcomments='\n'.join([ '{indent}\'{line}{linebreak}'.format(indent=q_indent,line=line,linebreak="\n") for line in q_comments_global]),partbegin=q_categorical_beginning,partstubs=q_categorical_stubs_updfrommatching,partend=q_categorical_end)
        else:
            return t_input
            
    
    t_parts = split_linebreaks(trim_linebreaks(t))
    #t_debug = [ print('part: "{part}"'.format(part=tempprintformat(t,chars=45))) for t in t_parts ]
    t_parts_processed = [ process_part(part) for part in t_parts ]
    t_clean = "\n" + ("\n\n\n".join(t_parts_processed)) + "\n"
    return t_clean
    #return "beautiful meta!"



def beautify(t):
    
    print('beautify called!')
    
    #if re.search(re_patter_matching_metadata,t,flags=re.DOTALL|re.ASCII|re.I):
	#    print('metadata found, searches={searches}'.format(searches=re.search(re_patter_matching_metadata,t,flags=re.DOTALL|re.ASCII|re.I).group()))
    #else:
    #    print('metadata not found')
    #
    
    s = re.search(re_patter_matching_metadata,t,flags=re.DOTALL|re.ASCII|re.I)
    print('meta begin = "{begin}", meta body="{body}", meta end="{end}"'.format(begin=tempprintformat(s[1],chars=15),body=tempprintformat(s[2],chars=25),end=(tempprintformat(s[3],chars=25))))
    print('searching in "{end}"'.format(end=(tempprintformat(s[3],chars=85))))
    s = re.search(re_patter_matching_onnextcase,s[3],flags=re.DOTALL|re.ASCII|re.I)
    print('onnextcase begin = "{begin}", onnextcase body="{body}", onnextcase end="{end}"'.format(begin=tempprintformat(s[1]),body=tempprintformat(s[2]),end=(tempprintformat(s[3]))))
    
    t = re.sub(r'\r?\n',"\n",t,flags=re.DOTALL|re.ASCII|re.I)
    
    t = re.sub(
        re_patter_matching_metadata,
        lambda matches_metadata: '{begin}{body}{end}'.format(
            begin = matches_metadata[1],
            body = confirm_trailing_linebreak( beautify_metadata( matches_metadata[2] ) ),
            end = re.sub(
                re_patter_matching_onnextcase,
                lambda matches_onnextcase: '{begin}{body}{end}'.format(
                    begin = matches_onnextcase[1],
                    body = confirm_trailing_linebreak( beautify_onnextcase( matches_onnextcase[2] ) ),
                    end = matches_onnextcase[3]
                ),
                matches_metadata[3],
                flags = re.DOTALL|re.ASCII|re.I
            )
        ),
        t,
        flags=re.DOTALL|re.ASCII|re.I
    )
    
    t = re.sub(r'\r?\n',"\n",t,flags=re.DOTALL|re.ASCII|re.I)
    
    return t


def beautify_working_file(t):
    
    print('beautify working file called!')
    
    s = re.search(re_patter_matching_metadata,t,flags=re.DOTALL|re.ASCII|re.I)
    if s:
        t = '{begin}{upd}{end}'.format(begin=s[1],upd=beautify_working_metadata(s[2]),end=s[3])
    else:
        t = '{begin}{upd}{end}'.format(begin='',upd=beautify_working_metadata(t),end='')
    
    return t


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
    out_file_specs_name = '{prev_name}{added_part}'.format(prev_name=inp_file_specs_name,added_part='.beautiful.mrs')
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
