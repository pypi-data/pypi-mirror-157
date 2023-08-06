import React from "react";
import { Text } from "@ui-kitten/components";
import { View } from "react-native";

export default class ScreenTwo extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    return (
      <View
        style={{
          height: "100%",
          justifyContent: "center",
          alignItems: "center",
          flex: 1,
        }}
      >
        <Text>World</Text>
      </View>
    );
  }
}
