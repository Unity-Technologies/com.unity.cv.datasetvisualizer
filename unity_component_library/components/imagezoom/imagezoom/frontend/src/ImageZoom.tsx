import {
  Streamlit,
  withStreamlitConnection,
  StreamlitComponentBase
} from "streamlit-component-lib"
import React, { ReactNode} from "react"
import IconButton from '@material-ui/core/IconButton';
import ArrowForwardIosIcon from '@material-ui/icons/ArrowForwardIos';
import { styled, TextField, Dialog, DialogTitle} from "@material-ui/core"


class ImageZoom extends StreamlitComponentBase {
  public render = (): ReactNode => {
    return (
      <div style={{
        position: "absolute",
        left: "50%",
        top: "50%",
        width: "90%",
        height: "90%"
      }}>
        <div style={{
          backgroundColor: "red",
          position: "relative",
          left: "-50%",
          top: "-50%",
          width: "100%",
          height: "100%"
        }}>
          hello
        </div>
      </div>
    )
  }
}

export default withStreamlitConnection(ImageZoom)

