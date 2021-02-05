import * as React from "react"
import { makeStyles, Paper, Typography } from "@material-ui/core"
import { message } from "../message/message"

const useStyles = makeStyles({
    container: {
        padding: "10px",
        margin: "20px",
    },
    msg_left: {
        marginRight: "60px"
    },
    msg_right: {
        marginLeft: "60px"
    },
});

export default function ChatMessage({msg} : {msg: message}) {
    const classes = useStyles();

    return (
        <Paper className={[classes.container, msg.from ? classes.msg_left : classes.msg_right].join(" ")}>
            <Typography variant="caption">
                {msg.from ? "Virtual Agronomist" : "You"} - {msg.time.toLocaleTimeString().substr(0,5)}
            </Typography>
            <Typography variant="body1">
                {msg.text}
            </Typography>
        </Paper>
    )
}