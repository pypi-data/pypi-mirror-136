# createmeal-py
A HTML library renderer.


## Get Started

Instalation

    pip install createmeal-py



## Basic Usage

The main metod of createmeal is toHtml({}), so:

        print(createmeal.toHtml({div:{}}))
        
output:
        
        <div></div>



Take a Hello world example:

        helloWorld = {
            html:{
                head: {},
                body: {
                    div: [
                        {
                            h3: ["Hello World!"]
                        },
                        {
                            p: ["This is a simple way to generate DOM without write HTML."]
                        }
                    ]
                }
            }
        }
            
        print(createmeal.toHtml(helloWorld));

output:

    <html>
        <head>
        </head>
        <body>
            <div>
                <h3>Hello World!</h3>
                <p>This is a simple way to generate DOM without write HTML.</p>
            </div>
        </body>
    </html>


## Build
Make sure you have the latest version of PyPA’s build installed:

    python3 -m pip install --upgrade build

Now run this command from the same directory where pyproject.toml is located:

    python3 -m build


## Documentation
You can find the createmeal documentation [on the website](https://createmeal.org/).

## License

Createmeal is [MIT licensed](./LICENSE).