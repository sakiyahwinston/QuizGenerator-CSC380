# QuizBot


In to get this app working, you should first download the zip file by going to the green "Code" button above and clicking "Download ZIP". After downloading, you should unzip the file to the working directory of your choice. If you haven't already done so at some point, you will need to open the microsoft store app and install Python 3.11 in order for the installer to work. The program should be able to work with other python versions, but you will need to set up your own environment and run it yourself. After running the installer and getting your key(instruction below) you should be able to run the start file and have it work.

Since the app is based off of ChatGPT, you will need to get an API key in order for it to work past launching the interface. Next are instructions to generate a free key through github. If you get yourself a key through OpenAI, there will be a note at the bottom on how to get it working.

You can generate yourself a free key through github which will need an account for. Go to the following link
https://github.com/marketplace/models/azure-openai/gpt-4o
and click the green "Use this model" button, a new menu will pop up. Click on the green "Create Personal Access Token" button. This will begin key creation. You can name the key whatever you want but there are a few necessary things to enable.
You can choose the expiration date of your key, but it isn't a great idea to give it no expiration for security reasons. On top of this, don't be sharing your key around.
Make sure that repository access is set to "Public Repositories". For permissions, the only one that should be needed is "Models". After this, you can generate your token. MAKE SURE YOU SAVE THIS TOKEN SOMEWHERE. You cannot just come back to github to see it.
Finally to use your new key, go to the folder where you unzipped this repository. Create a file called .env(make sure it isn't .env.txt or something) and put the following inside:

OPENAI_API_KEY='Your Key Goes Here' 

base_url='https://models.inference.ai.azure.com'

Replacing 'Your Key Goes Here' with the key you just created. With this done, you should be able to run the app by executing the "main.py" file.
If you are using a key from OpenAI instead of Github, all you should need to change is the value for 'base_url' in the .env file. I don't actually know the specific url but it should be somewhere on their website.

If you get the app working and occasionally see Error Code: 400, this isn't a problem with your setup. This seems to only happen with the github keys and I'm not sure how to resolve it yet.
