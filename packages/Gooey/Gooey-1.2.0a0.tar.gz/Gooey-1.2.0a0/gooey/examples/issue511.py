from textwrap import dedent

from gooey import Gooey, GooeyParser


@Gooey(program_name='My Super Awesome Program',
       default_size=(670, 615),
       header_show_title=True,
       dump_build_config=True,
       menu=[{
           'name': 'Help',
           'items': [{
               'type': 'Link',
               'menuTitle': 'Visit Our Site',
               'url': 'https://github.com/chriskiehl/Gooey'
           }, {
               'type': 'MessageDialog',
               'menuTitle': 'Visit Our Site',
               'message': 'Hello world!!!!'
           }, {
               'type': 'HtmlDialog',
               'menuTitle': 'Fancy About',
               'caption': 'Custom Dialog with basic HTML support',
               'html': dedent(r'''
                            <div align="center">
                                <img width="60" height="60" src="C:\Users\Chris\Documents\Gooey\gooey\images\config_icon.png" /> 
                            </div>
                            
                           <h2>Hello there!</h2>
                           <p><font color="red">I am </font>  
                           <font color="blue">some </font>
                           <font color="green">custom</font>
                           <font color="purple">html!</font>  
                           '''),
           }]
       }]
       )
def main():
    '''
    Dummy Function to create a gooey GUI and test the issue.
    '''
    parser = GooeyParser(
        description='This is my program.\nThere are many like it, but this one is mine.')
    parser.add_argument('myfolder', widget='DirChooser',
                        help='Path to directory where output will be stored.')
    args = parser.parse_args()

    print('I\'m a dummy!')


main()