import * as React from "react"
import { CssBaseline, Typography } from "@material-ui/core"

export default function HaystackAnnotation() {
    return (
        <div>
            <CssBaseline />
            <Typography variant="h2">
                Logs
            </Typography>
            <Typography paragraph>
                From this page you're able to download complete system logs including timestamps, questions and given answers. Logs committed to the database every time a user interacts with the system.
                A complete log file is downloaded from this page.
            </Typography>
            <Typography variant="h2">
                Usage
            </Typography>
            <Typography paragraph>
                This page displays usage statistics from the system including total queries over different time periods and a graph of queries over time.
            </Typography>
            <Typography variant="h2">
                Training
            </Typography>
            <Typography paragraph>
                The training page allows you to train the system.
                The question answer section displays questions users have asked and the answer given by the system / the answer the user selected as most apropriate.
                You are then able to verify the answer given, choose a better answer or simply throw away the data. All verified data can then be submitted to the system and used as training data.
                Once submitted you are not able to undo training so be carefull to submit only when you are happy with the training data you have checked.
            </Typography>
            <Typography variant="h2">
                Documents
            </Typography>
            <Typography paragraph>
                The documents page lets you upload, view and delete the knowledge documents currently in the system.
                You are able to upload text files containing information along with table data in the form of a csv file and an acompanying text file describing the table.
                Text documents are best formatted as simple paragprahs representing the answer to a single question. All context relevant to the question should be included in the answer such as crop types being asked about, relevant crop timings etc.
                Paragraphs should be seperated with newlines. Individual text documents can contain non related paragraphs but for ease of organising it's best to keep each documents about one topic.
                To delete a document, use the delete icon the right of the document. To replace a document simply delete the old one and reupload the new document. 
            </Typography>
        </div>
    )
}