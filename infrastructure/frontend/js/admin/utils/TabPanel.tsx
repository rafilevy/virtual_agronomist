import { Box } from "@material-ui/core";
import React from "react";

export const TabPanel : React.FunctionComponent<{value: number, index: number}> = (props) => {
    const {index, value, children, ...other} = props;

    return (
        <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
        >
        {value === index && (
            <Box p={3}>
                {children}
            </Box>
        )}
        </div>
    );
}