import * as React from "react"
import { makeStyles, Typography } from "@material-ui/core"
import { message } from "./message"

const useStyles = makeStyles({
    container: {
        padding: "10px",
        margin: "10px 20px",
        border: "1px dashed rgba(0, 0, 0, 0.13)"
    },
    msgLeft: {
        textAlign: "left",
        marginRight: "60px"
    },
    msgRight: {
        textAlign: "right",
        marginLeft: "60px"
    },
});

export default function StatusMessage({msg} : {msg: message}) {
    const classes = useStyles();

    return (
        <div className={[classes.container, msg.from ? classes.msgLeft : classes.msgRight].join(" ")}>
            <Typography variant="caption">
                {msg.text}
            </Typography>
        </div>
    )
}