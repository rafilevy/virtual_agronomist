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
            Logs include timestamps, questions and given answers. Logs are committed to the database every time a user completes a question answer cycle with the system.
            A complete log file can be downloaded from this page.
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
                To delete a document, use the delete icon the right of the document. To replace a document simply delete the old one and reupload the new document. 
            </Typography>
            <Typography variant="h4">
                Text-based Documents
            </Typography>
            <Typography paragraph>
                Any new text-based document should be reformatted such that each paragraph contains one knowledge point and is phrased independently with no reference to other paragraphs or contexts.
                The more relevant keywords mentioned, the better the document is defined and it will improve the accuracy when related questions are asked.
            </Typography>
            <Typography paragraph>
                For example, it is useful to explicitly mention if any specific fungicide is relevant to the discussion, or the timing currency in discussion.
                Mentioning key things defined in the categories.csv(refer to file format below) file will improve the accuracy in sensing the context of the paragraph.
            </Typography>
            <Typography paragraph>
                This file should be a .txt file with the name describing the contents.
                Explicit mentioning of a crop name is preferred as it will provide a clearer definition for the information.
                For example, the name of the file can be “Winter Wheat Fungicide.txt”.
            </Typography>
            <Typography variant="h4">
                Table Documents
            </Typography>
            <Typography paragraph>
            Any table based document should be a pair of .csv and .txt files with the same file name and describes information from one single table. Each entry in the csv should describe one row/column in the table.
            For example, the following table can be represented by the csv entries below:
            <img height="300px" src="http://localhost:3000/frontend/img/table.png"/>
            </Typography>
            <Typography paragraph>
                The associated .txt file should contain the description of the table. Following the example above, the .txt file can be:
                <br/>
                <img height="100px" src="http://localhost:3000/frontend/img/text0.png"/>
                <br/>
                The more specific the description, the more accurate it will be when a question about the table is asked. The connection between the description and the actual table is detected by the shared filename, but the filename itself does not matter. For example, table1.csv and table1.txt works just fine as valid filename and there is no difference if the pair is renamed to components.csv and components.txt.
                <br/>
                <img height="30px" src="http://localhost:3000/frontend/img/text1.png"/>
            </Typography>
            <Typography variant="h4">
                Keyword Extractor - <code>categories.csv</code>
            </Typography>
            <Typography paragraph>
            The keyword extractor is used to tag passages of text with pairs of categories and keywords, for example (crop: winter barley, winter wheat) is such a pair.
            In addition, the keyword extractor can provide a generic question for each category. To extract the correct keywords and their corresponding keywords, the file <code>categories.csv</code> is used. Each row of the csv file contains the information for one category. The information for each category is:
            <ul>
                <li>
                1 Category Name - (e.g. crop, fungicide)
                </li>
                <li>
                1 Generic Question - (e.g. Is there a specific crop that you would like to ask about?)
                </li>
                <li>
                1 or more values for this category - (e.g. spring wheat| winter wheat| spring beans)

                </li>
            </ul>
            </Typography>
            <Typography paragraph>
            In order to allow questions to contain commas, the separating character for this file is a pipe symbol (| ). This should come immediately after the end of a value. There should be no separating character at the end of a line. There can be spaces before a new value. Category names and values can be input in uppercase or lowercase, but all output will be in lowercase only.
                Below is an example of some truncated rows of a `categories.csv` file.
                <code>
                Crop| Is there a specific crop that you would like to ask about?| spring wheat| winter wheat| winter barley<br/>
                Disease| Is there a specific disease that you would like to ask about?| ramularia| septoria| rust| yellow rust<br/>
                Fungicide| Do you want to check for a specific fungicide?| opus| bowman| cortez| rubric| epic| corral| amber<br/>
                Timing| Is there a specific timing that you would like to ask about? (E.g. T0,T1,etc)| t0| t1| t2| t3| t4<br/>
                Area| Which area are you in? (E.g. east/north/etc)| east| north| southeast| west| south| southwest
                </code>
                Categories may be added by adding a new row with the required information.
            </Typography>
            <Typography variant="h4">
                Timing translator - <code>translation.csv</code>
            </Typography>
            <Typography paragraph>
            The timing translator is used to standardise crop timing names. It does this by grouping equivalent timing names together, within each crop. The translation.csv file is comma-separated. For each crop’s translation table, multiple rows are used. The information for each crop is:
            <ul>
                <li>
                1 unique Crop Name
                </li>
                <li>
                1 or more lists of equivalent timings
                    <ul>
                        <li>The first name should be unique within this crop</li>
                        <li>Each timing name is separated by a comma</li>
                    </ul>
                </li>
                <li>
                1 or more values for this category - (e.g. spring wheat| winter wheat| spring beans)

                </li>
            </ul>
            </Typography>
            <Typography paragraph>
            Each crop’s translation table is therefore represented by 2 or more lines. Translation tables should be separated by a blank line. Below is an example of timing tables for winter wheat and spring wheat.
            This extract shows a sample translation table for winter wheat. This translation table will standardise leaf 4 to T0 if the crop is known to be winter wheat. There can be more than one translation per line, for example replacing line 2 with T0, leaf 4, leaf four
            would lead to the translator standardising both leaf 4 and leaf four to T0. In the second table, no translations have been added.
            <br/>
            <code>
            Winter Wheat<br/>
            T0, leaf 4<br/>
            T1, leaf 3<br/>
            T1.5, leaf 2<br/>
            T2, flag leaf<br/>
            T3, ear<br/>
            T4, second ear<br/><br/>

            Spring Wheat<br/>
            T0<br/>
            T1<br/>
            T2<br/>
            T3<br/>
            </code>
            </Typography>

            <Typography variant="h4">
                Pressure Score Calculator - <code>pressure_score.csv</code>
            </Typography>
            <Typography paragraph>
            The pressure score calculator is used to calculate the pressure score of the user’s current situation based on a series of predefined questions. This will be triggered when different pressure scores are mentioned in the top extracted documents. The set of questions and scores related to each option is configurable with the pressure score.csv.
            </Typography>
            <Typography paragraph>
            Any question in the pressure score system is defined by multiple entries, each having four fields separated by a comma:
            <ul>
                <li>
                1 Crop Name - (e.g. winter wheat, winter barley)
                </li>
                <li>
                1 Factor - (e.g. area in the country, variety of crop, sowing date)
                </li>
                <li>
                1 Option - (e.g.(area in the country) East, West)
                </li>
                <li>
                1 Score related to the Option
                </li>
            </ul>
            </Typography>
            <Typography paragraph>
            Below is the example of a set of entries which forms a question for the pressure score calculation of winter wheat.
            <br/>
            <code>
            winter wheat,area in the country,East,1<br/>
            winter wheat,area in the country,North,2<br/>
            winter wheat,area in the country,South East,2<br/>
            winter wheat,area in the country,West,3<br/>
            winter wheat,area in the country,South,3<br/>
            winter wheat,area in the country,South West,4<br/>
            </code>
            </Typography>
            <Typography paragraph>
            When the pressure score calculator is triggered for a question on winter wheat, these entries will form a question about the location of the user in the country. If the user responds with the East option, the current pressure score will be increased by 1. If the response is West, the pressure score will be increased by 3.
            </Typography>
            <Typography paragraph>
            When new entries are added to the file, the pressure score system will be updated and new questions can be asked.
            </Typography>
        </div>
    )
}