import * as React from "react"
import { Button, CssBaseline, makeStyles, Paper, Typography } from "@material-ui/core";
import AttachmentIcon from '@material-ui/icons/Attachment';

const useStyles = makeStyles({
});

export default function LogDownloadPage() {
    const classes = useStyles();

    return (
        <div>
            <CssBaseline />
            <Typography paragraph>
                <Button
                    href="http://localhost:8000/logs"
                    variant="contained"
                    color="primary"
                    startIcon={<AttachmentIcon />}
                >
                    Download Logs
                </Button>
            </Typography>
        </div>
    )
}