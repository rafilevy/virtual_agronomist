import * as React from "react"
import AdminPage from "./AdminPage";
import { createMuiTheme, ThemeProvider, useMediaQuery } from "@material-ui/core";

function App() {
    const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');

    const lightTheme = createMuiTheme({
        palette: {
            type: "light",
        }
    });
    const darkTheme = createMuiTheme({
        palette: {
            type: "dark",
        }
    });

    const [theme_, setTheme_] = React.useState(prefersDarkMode);
    const toggleTheme = () => setTheme_(!theme_);

    return (
        <ThemeProvider theme={!theme_ ? darkTheme : lightTheme}>
            <AdminPage toggleTheme={toggleTheme}/>
        </ThemeProvider>
    )
}

export default App;