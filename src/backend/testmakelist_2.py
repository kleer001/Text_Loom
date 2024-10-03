# testing intigration of make_list and looper and query and file_out


create text_chars type text
text_chars parm text "please give me a simple list of five stereotypical modern japanese characters from every day life."

create text_stories type text
text_stories parm text "please give me a simple list of five aesop fables that feature only one animal."

create looper1 type looper
create merge1 type merge 

merge1 input to text_chars
merge1 input to text_stories
looper1 input to merge1
merge1 parm single_string False #merge to string list


create text_prompt type text inside looper
text_prompt_A input to looper._input_null 
text_prompt_A parm text "Given the character of $N "


file_out to merge #for printing
file_out export loop_list_book.txt #to parm