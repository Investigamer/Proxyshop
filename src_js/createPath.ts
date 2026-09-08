import { app, core, constants } from "photoshop";
import { type PathPointInfo } from "photoshop/dom/objects/PathPointInfo";

interface PointConf {
  x: number;
  y: number;
}

interface PathPointConf extends PointConf {
  left?: PointConf;
  right?: PointConf;
}

const data: PathPointConf[] = [];

function createPath(points: PathPointConf[]) {
  const infoPoints: PathPointInfo[] = [];
  for (const point of points) {
    const info = new app.PathPointInfo();
    info.anchor = [point.x, point.y];
    info.kind =
      point.left || point.right
        ? constants.PointKind.SMOOTHPOINT
        : constants.PointKind.CORNERPOINT;
    info.leftDirection = point.left
      ? [point.left.x, point.left.y]
      : info.anchor;
    info.rightDirection = point.right
      ? [point.right.x, point.right.y]
      : info.anchor;
    infoPoints.push(info);
  }
  const subPath = new app.SubPathInfo();
  subPath.closed = true;
  subPath.operation = constants.ShapeOperation.SHAPEADD;
  subPath.entireSubPath = infoPoints;
  const newPath = app.activeDocument.pathItems.add("New Path", [subPath]);
  newPath.select();
}

core.executeAsModal(async () => createPath(data), {
  commandName: "Programmatic Create Path",
});
