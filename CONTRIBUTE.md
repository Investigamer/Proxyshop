# How to Contribute to Proxyshop
1. Firstly, follow the Python installation instructions to get a proper development environment setup correctly. At this time Python 3.10 is recommended.
2. One of Proxyshop's dependencies is a tool called **Commitizen**. When you make commits to your fork with the 
intention of contributing to the main Proxyshop repo, you need to use commitizen to make these commits. Commitizen 
enforces [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), tracks version changes, and helps us automatically generate accurate changelogs.
3. Start by staging your changes:
`git add filename.py` - This will stage one file
`git add path/to/filename.py` - This will stage a file in a directory
`git add .` - This will stage every file that has changed
You can also see files that have changed, or files that are currently staged with: `git status` or unstage all files with `git reset`
4. Commit your changes with commitizen using `cz commit`. Commitizen will now take you through some prompts to put together the perfect commit. Let's look at each part of this process:
> **Select the type of change you are commiting**
> You're presented with a multiple choice selection. The descriptions are pretty self-explanatory, you can google them up for deeper explanation.
> *Example: fix*
> 
> **What is the scope of this change?**
> This can be a function, a class, a filename (such as templates.py), or if the changes happen in multiple files but affect the same feature it can be a feature, for example "updater" or "console" or "gui", etc.
> *Example: scryfall*
> 
> **Write a short and imperative summary of the code changes**
> Keep this short and sweet! You have plenty of room in the description, so use brevity but explain the basic thing you are fixing or adding.
> *Example: Download art scan bug*
> 
> **Provide additional contextual information about the code changes**
> Here you might wanna explain more details for what was causing the issue, or additional changes that were rolled into the commit, or things this change might effect, etc use your imagination.
> *Example: Implemented try/catch retry system for when Scryfall fails to retrieve the art scan*
> 
> **Is this a BREAKING CHANGE?**
> 9 times out of 10 you just want to hit enter to skip this step (automatically inputs N for no). A breaking change is when a code change you've made causes other features in the app to break or causes the app to no longer be backward compatible. In our case, a breaking change would mean old templates and plugins made by creators will NOT work with the changes you've made. Unless you are a major contributor, you probably shouldn't be making breaking changes unless you've come up with a revolutionary new idea. Breaking changes aren't fun. Use your best judgement.
> *Example: Just press enter*
> 
> **Footer.**
> Most of the time you probably just want to hit enter to skip this step. Alternatively, you might want to reference an issue raised on the Proxyshop issues section, you can reference issues using #, such as #23. You could also sign your name here, list any breaking changes or any parting notes of importance.
> *Example: Addresses Issue #23*

You've just made your first **Commitizen** commit! Now push it up to Github with `git push`. Now you're ready to put in a Pull Request!