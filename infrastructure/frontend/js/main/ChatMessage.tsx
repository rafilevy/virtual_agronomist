import * as React from "react"
import { IconButton, makeStyles, Paper, Typography } from "@material-ui/core"
import { message } from "./message"
import { ReportSharp } from "@material-ui/icons";
import { red } from '@material-ui/core/colors';

const useStyles = makeStyles({
    container: {
        padding: "10px",
        margin: "20px",
        display: "flex"
    },
    msg_left: {
        marginRight: "60px"
    },
    msg_right: {
        marginLeft: "60px"
    },
    message: {
        flexGrow: 1
    }
});

export default function ChatMessage({msg, onReport, latest} : {msg: message, onReport?: () => void, latest: boolean}) {
    const classes = useStyles();

    return (
        <Paper className={[classes.container, msg.from ? classes.msg_left : classes.msg_right].join(" ")}>
            <div className={classes.message}>
                <Typography variant="caption">
                    {msg.from ? "Virtual Agronomist" : "You"} - {msg.time.toLocaleTimeString().substr(0,5)}
                </Typography>
                <Typography variant="body1">
                    {msg.text}
                </Typography>
            </div>
            {latest && msg.canReport && 
                (<div style={{
                    alignSelf: "stretch",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                }}>
                    <IconButton aria-label="delete" onClick={() => onReport && onReport()}>
                        <ReportSharp style={{ color: red[500] }} />
                    </IconButton>
                </div>)
            }
        </Paper>
    )
}