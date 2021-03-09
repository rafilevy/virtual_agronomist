# Frontend

The frontend is built with Typescript and React.js and uses the Material-UI component library for styling.

The frontend container compiles the react files using webback and serves them from localhost:3000. During development the frontend container can be launched to allow for working on the frontend without having to deploy all the backend containers. To do so, serve and then navigate to the `dev/main.html` or `dev/admin.html` pages to view the main and admin insights pages respectively.

## File overview

### Configuration Files

`tsconfig.json` provides settings for the typescript compilation and error checking of the frontend code.

`Dockerfile` contains the docker command that is executed when the frontend container is launched.

`sass/` contains the root scss styles for all pages. This is not currently used much in our implementation.

### UI Code

`reportWebVitals.ts` is Boilerplate code which can measure performance of the react app. To activate logging the function it exposes can be called from the apps entrypoint files (`admin.tsx` or `main.tsx`).

`index.tsx` - The entrypoint for the user page. Simply wraps the `main/App` component.

`login.tsx` - The login page, routed to if someone attempts to access the admin page and is not logged in. From here the user is able to authenticate with django and is then routed to the admin page.

`admin.tsx` - The entrypoint for the admin page. Simply wraps the `admin/App` component.

#### User Frontend Components
`main/App.tsx` - A wrapper of the MainPage component

`main/MainPage.tsx` - The main user page, defines the layout of the messages and text entry box. Contains code for making API calls to allow the user to send questions to the backend and displays the answers.

`main/ChatMessage.tsx` - A react component showing a single chat message sent between the user and the virtual agronomist.

`main/MultiMessage.tsx` - A react component showing a message sent from the virtual agronomist which contains options the user is able to select.

`main/StatusMessage.tsx` - A react component displaying a status message from the system.

`main/message.ts` - Typescript type declarations describing the json messages received from the backend.

#### Admin Frontend Components
`admin/App.tsx` - A wrapper of the AdminPage component.

`admin/AdminPage` - The admin insights page, contains a small amount of code allowing the user to route between the subpages.

`admin/subpages` - Contains all the subpages of the admin insights page.

`subpages/OverviewPage.tsx` - An overview page describing each of the subpages, what they do and how to use them.

`subpages/DocumentsPage.tsx` - A page allowing the user can upload documents to the knowledge base.

`subpages/LogDownloadPage.tsx` - A page for downloading the system logs from the backend.

`subpages/UsagePage.tsx` - A page for viewing system usage. Displays total queries in given time periods and graph of system usage over time.

`subpages/TrainingPage.tsx` - A page allowing the admin to review training data being fed to the pipeline. Is able to review answers the system has given and ones users have reported and select better answers before committing the information as training data to the pipeline to be trained on.