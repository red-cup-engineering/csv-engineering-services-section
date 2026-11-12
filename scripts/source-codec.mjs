import { decodeUtf8Source, defineSourceCodec, encodeUtf8Source } from "@red-cup-engineering/signcell/source-codec";
import { csvToJson, jsonToCsv } from "./csv-codec.mjs";

export const csvSourceCodec = defineSourceCodec({
  id: "csv.records/v1", mediaType: "text/csv", maxBytes: 65536, valueIdentity: "exact",
  decode: bytes => csvToJson({ text: decodeUtf8Source(bytes) }),
  encode: value => encodeUtf8Source(jsonToCsv(value).text),
});
