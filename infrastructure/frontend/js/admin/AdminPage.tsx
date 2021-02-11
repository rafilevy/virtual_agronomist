import * as React from "react"
import { AppBar, Box, Button, Container, CssBaseline, Divider, Drawer, IconButton, List, ListItem, ListItemIcon, ListItemText, makeStyles, Paper, TextareaAutosize, Toolbar, Typography, useTheme } from "@material-ui/core"
import OverviewPage from "./subpages/OverviewPage";
import BrightnessHigh from "@material-ui/icons/BrightnessHigh";
import Brightness3 from "@material-ui/icons/Brightness3";


const drawerWidth = 240;
const useStyles = makeStyles((theme)=> ({
    root: {
        width: "100%",
        height: "100%",
        display: "flex"
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
    },
    titleText: {
        flexGrow: 1
    },
    drawer: {
        width: drawerWidth,
        flexShrink: 0
    },
    drawerPaper: {
        width: drawerWidth
    },
    drawerContainer: {

    },
    content: {
        flexGrow: 1,
        backgroundColor: theme.palette.background.default,
        padding: theme.spacing(3)
    }
}));

// const ws_scheme = window.location.protocol == 'https:' ? 'wss' : 'ws';
// const socketUrl = `${ws_scheme}://${location.host}/ws/chat/`;


function AdminPage({toggleTheme} : {toggleTheme : ()=>void} ) {
    const classes = useStyles();
    const theme = useTheme();

    const pages = ["Overview", "Logs", "Performance", "Usage"] as const;
    const [currentPage, setCurrentPage] = React.useState<typeof pages[number]>("Overview");

    return (
        <div className={classes.root}>
            <AppBar position="fixed" className={classes.appBar}>
                <Toolbar>
                    <Typography className={classes.titleText} variant="h6">
                        Admin Insights
                    </Typography>
                    <IconButton onClick={()=>toggleTheme()}>
                        {theme.palette.type == "dark" ? <BrightnessHigh /> : <Brightness3 />}
                    </IconButton>
                </Toolbar>
            </AppBar>
            <Drawer className={classes.drawer} variant="permanent" classes={{paper: classes.drawerPaper}}>
                <Toolbar />
                <div className={classes.drawerContainer}>
                    <List>
                        {pages.map((text, index) => (
                        <ListItem button key={text} onClick={()=>{setCurrentPage(text)}}>
                            <ListItemText primary={text} />
                        </ListItem>
                        ))}
                    </List>
                </div>
            </Drawer>
            <main className={classes.content}>
                <Toolbar />
                { 
                    currentPage === "Overview" && <OverviewPage /> 
                    || currentPage === "Logs" && <Typography>LOGS</Typography>
                }
            </main>
        </div>
    )
}

export default AdminPage;