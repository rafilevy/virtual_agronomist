import * as React from "react"
import { Box, CssBaseline, Divider, Grid, makeStyles, Paper, Tab, Tabs, Typography, useTheme,  } from "@material-ui/core"

const useStyles = makeStyles((theme) => ({
    paper: {
        padding: theme.spacing(2),
    },
    paperTitle: {
        textAlign: "center"
    },
    paperText: {
        paddingTop: theme.spacing(2),
    }
}));

// const TabPanel : React.FunctionComponent<{value: number, index: number}> = (props) => {
//     const {index, value, children, ...other} = props;

//     return (
//         <div
//         role="tabpanel"
//         hidden={value !== index}
//         id={`simple-tabpanel-${index}`}
//         aria-labelledby={`simple-tab-${index}`}
//         {...other}
//         >
//         {value === index && (
//             <Box p={3}>
//                 {children}
//             </Box>
//         )}
//         </div>
//     );
// }


export default function KeywordsPage() {
    const classes = useStyles();
    const theme = useTheme();

    const [graphTabValue, setGraphTabValue] = React.useState(0);
    const handleGraphTabChange = (_ : any, newVal : number) => setGraphTabValue(newVal);

    return (
        <div>
            <CssBaseline />
            <Grid container spacing={2}>
                <Grid item xs>
                    <Paper className={classes.paper}>
                    </Paper>
                </Grid>
                <Grid item xs>
                    <Paper>
                    </Paper>
                </Grid>
            </Grid>
        </div>
    )
}