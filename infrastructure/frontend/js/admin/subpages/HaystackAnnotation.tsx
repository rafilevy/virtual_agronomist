import * as React from "react"
import { CssBaseline, Link, makeStyles, Paper, Typography } from "@material-ui/core"

export default function HaystackAnnotation() {
    return (
        <div>
            <CssBaseline />
            <Typography paragraph>
                To add annotations to the documents head <Link href="https://annotate.deepset.ai/login" target="_blank">here</Link>.
            </Typography>
        </div>
    )
}